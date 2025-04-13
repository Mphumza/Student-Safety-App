from flask import Flask, render_template, redirect, url_for, request, session,jsonify
from firebase_setup import db, auth  
from firebase_admin import firestore 
from firebase_setup import upload_image_to_imgbb
from werkzeug.security import check_password_hash , generate_password_hash
from qr_code import generate_qr 
import uuid
import os
from waitress import serve
import logging
from datetime import timezone
from flask_mail import Mail
from qr_code import delete_child
from flask import Flask, render_template, request, redirect, url_for, flash
import re  
import pytz # type: ignore

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'student tracker'  

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/qr_code/<child_id>')
def get_qr_code(child_id):
    return generate_qr(child_id)  


@app.route('/delete_child/<child_id>', methods=['POST'])
def delete_child_route(child_id):
   
    if 'admin_email' not in session:
        flash('You must be logged in.', 'danger')
        return redirect(url_for('login'))  

    delete_child(child_id)
    return redirect(url_for('dashboard', admin_email=session['admin_email']))


def email_exists(collection, email):
    doc = db.collection(collection).document(email).get()
    return doc.exists


@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()  
    if request.method == 'POST':
        admin_email = request.form['email']
        admin_name = request.form['name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match.")

        # Prevent duplicate admin registration using Firestore
        existing_admin = db.collection('admins').where('email', '==', admin_email).get()
        if existing_admin:
            return render_template('register.html', error="This email is already registered as an admin.")

        admins = db.collection('admins').get()

       
        if len(admins) >= 5:
            return render_template('register.html', error="The maximum number of admins (5) has been reached.")

        is_main_admin = len(admins) == 0 
        try:
            # Create user in Firebase Authentication using Pyrebase
            user = auth.create_user_with_email_and_password(admin_email, password)

            # Hash the password before storing it in Firestore
            hashed_password = generate_password_hash(password)

            db.collection('admins').document(admin_email).set({
                'name': admin_name,
                'email': admin_email,
                'password': hashed_password,
                'is_main_admin': is_main_admin
            })

            return redirect(url_for('dashboard'))
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                error_message = "This email is already registered."
            return render_template('register.html', error=error_message)

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email_exists('admins', email):
            return render_template('login.html', error="Admin account not found.")

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['admin_email'] = email
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('login.html', error="Invalid email or password.")

    return render_template('login.html')

# ---------- Admin Dashboard ----------
@app.route('/dashboard')
def dashboard():
    if 'admin_email' not in session:
        return redirect(url_for('login'))

    unread_reports_count = get_unread_reports_count()
    parents_ref = db.collection('parents')
    parents = parents_ref.stream()

    reports_ref = db.collection('reports')
    reports = reports_ref.stream()

    parent_reports = {}
    all_reports = []

    # South Africa time zone
    sa_tz = pytz.timezone("Africa/Johannesburg")

    for report in reports:
        report_data = report.to_dict()
        parent_email = report_data['parent_email']

        # Format timestamp if it exists
        timestamp = report_data.get('timestamp')
        if timestamp:
            timestamp_utc = timestamp.replace(tzinfo=timezone.utc)
            timestamp_local = timestamp_utc.astimezone(sa_tz)
            formatted_timestamp = timestamp_local.strftime('%B %d, %Y - %I:%M %p')
        else:
            formatted_timestamp = 'N/A'

        report_data['timestamp_formatted'] = formatted_timestamp

        parent_doc = db.collection('parents').document(parent_email).get()
        parent_data = parent_doc.to_dict() if parent_doc.exists else None

        all_reports.append({
            'report': report_data,
            'parent': parent_data,
            'id': report.id
        })

        parent_reports.setdefault(parent_email, []).append(report_data)

    return render_template('dashboard.html',
                           admin_email=session['admin_email'],
                           unread_reports_count=unread_reports_count,
                           parents=parents,
                           parent_reports=parent_reports,
                           reports=all_reports)

@app.route('/register_parent', methods=['GET', 'POST'])
def register_parent():
    session.clear()  # Clear session to prevent previous user from staying logged in
    if request.method == 'POST':
        parent_email = request.form['email']
        parent_name = request.form['name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']
        children = request.form.get('children', '')

        if password != confirm_password:
            flash("Passwords do not match.", 'error')
            return redirect(url_for('register_parent'))

        if not re.match(r'^0\d{9}$', phone):
            flash("Invalid phone number format.", 'error')
            return redirect(url_for('register_parent'))

        if email_exists('parents', parent_email):
            flash("This email is already registered as a parent.", 'error')
            return redirect(url_for('register_parent'))

        if email_exists('admins', parent_email):
            flash("This email is already registered as an admin.", 'error')
            return redirect(url_for('register_parent'))

        try:
            user = auth.create_user_with_email_and_password(parent_email, password)

            # Save parent data
            children_dict = {}
            for child_name in children.split(','):
                child_name = child_name.strip()
                if child_name:
                    child_id = str(uuid.uuid4())
                    children_dict[child_id] = {
                        'name': child_name,
                        'qr_code': url_for('get_qr_code', child_id=child_id, _external=True)
                    }

            db.collection('parents').document(parent_email).set({
                'name': parent_name,
                'email': parent_email,
                'phone': phone,
                'children': children_dict
            })

            flash("Parent registered successfully!", 'success')
            return redirect(url_for('parent_dashboard'))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
            return redirect(url_for('register_parent'))

    return render_template('register_parent.html')


@app.route('/login_parent', methods=['GET', 'POST'])
def login_parent():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email_exists('parents', email):
            return render_template('login_parent.html', error="Parent account not found.")

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['parent_email'] = email
            return redirect(url_for('parent_dashboard'))
        except Exception as e:
            return render_template('login_parent.html', error="Invalid email or password.")

    return render_template('login_parent.html')

# ---------- Parent Dashboard ----------
@app.route('/parent_dashboard')
def parent_dashboard():
    """Displays the parent's dashboard with child details."""
    if 'parent_email' not in session:
        flash('You must be logged in.', 'danger')
        return redirect(url_for('login_parent'))

    parent_email = session['parent_email']
    
    # Fetch parent document from Firestore
    parent_doc = db.collection('parents').document(parent_email).get()

    if parent_doc.exists:
        parent_data = parent_doc.to_dict()
        children = parent_data.get('children', {})  # Ensure children data is retrieved safely
        return render_template('parent_dashboard.html', parent=parent_data, children=children)

    flash('Parent data not found.', 'danger')
    return redirect(url_for('login_parent'))

import re
from flask import flash, redirect, request, session, url_for

def sanitize_child_id(child_id):
    """Sanitize the child ID to ensure it's a valid field name."""
    child_id = re.sub(r'[^a-zA-Z0-9_-]', '', child_id)
    return child_id.replace('-', '_')

@app.route('/edit_child/<child_id>', methods=['POST'])
def edit_child(child_id):
    """Updates the child's name directly from the dashboard."""
    if 'parent_email' not in session:
        flash('You must be logged in.', 'danger')
        return redirect(url_for('login_parent'))

    parent_email = session['parent_email']
    parent_ref = db.collection('parents').where('email', '==', parent_email).get()

    if not parent_ref:
        flash('Parent data not found.', 'danger')
        return redirect(url_for('parent_dashboard'))

    sanitized_child_id = sanitize_child_id(child_id)
    new_name = request.form['child_name']

    try:
        parent_ref[0].reference.update({f'children.{sanitized_child_id}.name': new_name})
        flash('Child name updated successfully!', 'success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')

    return redirect(url_for('parent_dashboard'))

@app.route('/deactivate_child/<child_id>', methods=['POST'])
def deactivate_child(child_id):
    """Marks a child as inactive instead of deleting from the database."""
    if 'parent_email' not in session:
        flash('You must be logged in.', 'danger')
        return redirect(url_for('login_parent'))

    parent_email = session['parent_email']
    parent_ref = db.collection('parents').where('email', '==', parent_email).get()

    if not parent_ref:
        flash('Parent data not found.', 'danger')
        return redirect(url_for('parent_dashboard'))

    sanitized_child_id = sanitize_child_id(child_id)

    try:
        parent_ref_doc = db.collection('parents').document(parent_ref[0].id)
        parent_ref_doc.update({f'children.{sanitized_child_id}.is_active': False})
        flash('Child deactivated successfully!', 'success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')

    return redirect(url_for('parent_dashboard'))



# ---------- Report Incident ----------
@app.route('/report_incident', methods=['GET', 'POST'])
def report_incident():
    if 'parent_email' not in session:
        flash('You must be logged in.', 'danger')
        return redirect(url_for('login_parent'))

    if request.method == 'POST':
        parent_email = session['parent_email']
        incident_type = request.form['incident_type']
        incident_description = request.form['incident_description']
        incident_location = request.form['incident_location']
        incident_image = request.files['incident_image']

        image_url = None
        if incident_image and incident_image.filename != '':
            image_url = upload_image_to_imgbb(incident_image)

        # Create the report data
        report_data = {
            'parent_email': parent_email,
            'incident_type': incident_type,
            'incident_description': incident_description,
            'incident_location': incident_location,
            'incident_image': image_url,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'read': False 
        }

        db.collection('reports').add(report_data)
        flash('Incident reported successfully!', 'success')
        return redirect(url_for('parent_dashboard'))

    return render_template('report_incident.html')


# ---------- Get Unread Reports Count ----------
def get_unread_reports_count():
    """Fetch the count of unread reports."""
    reports_ref = db.collection('reports').where('read', '==', False)
    unread_count = sum(1 for _ in reports_ref.stream())
    return unread_count


# ---------- Get Unread Reports (Grouped) ----------
@app.route('/get_unread_reports', methods=['GET'])
def get_unread_reports():
    """Fetch unread reports grouped by parent and mark them as read."""
    reports_ref = db.collection('reports').where('read', '==', False).stream()
    unread_reports = {}

    for report in reports_ref:
        data = report.to_dict()
        data['id'] = report.id  # Store report ID for reference
        parent_email = data.get('parent_email', 'Unknown')

        # Mark the report as read by updating the 'read' field in Firestore
        db.collection('reports').document(report.id).update({'read': True})

        if parent_email not in unread_reports:
            unread_reports[parent_email] = {'parent_name': parent_email, 'reports': []}

        unread_reports[parent_email]['reports'].append({
            'id': data['id'],
            'incident_type': data['incident_type'],
            'incident_description': data['incident_description'],
            'incident_location': data['incident_location'],
            'incident_image': data.get('incident_image'),
            'timestamp': data['timestamp']
        })

    # Return reports grouped by parent email
    return jsonify({
        'reports': list(unread_reports.values()),
        'unread_count': sum(len(parent['reports']) for parent in unread_reports.values())
    })

@app.route('/delete_report/<report_id>', methods=['POST'])
def delete_report(report_id):
    try:
        print(f"Attempting to delete report: {report_id}")  # Debug print
        db.collection('reports').document(report_id).delete()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Failed to delete report: {e}")  # Also print the error
        return jsonify({'status': 'error', 'message': str(e)})


# ---------- Mark Individual Report As Read ----------
@app.route('/mark_report_as_read/<report_id>', methods=['POST'])
def mark_report_as_read(report_id):
    """Mark a specific incident report as read."""
    try:
        db.collection('reports').document(report_id).update({'read': True})
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    


@app.route('/safety_tips')
def safety_tips():
    return render_template('safety_tips.html')

@app.route('/contact_support')
def contact_support():
    return render_template('contact_support.html')

@app.route('/update_parent_profile', methods=['POST'])
def update_parent_profile():
    """Updates parent's name, email, and children's data (edit & add)."""
    if 'parent_email' not in session:
        flash("You must be logged in to update your profile.", 'error')
        return redirect(url_for('login_parent'))

    parent_email = session['parent_email']
    parent_ref = db.collection('parents').where('email', '==', parent_email).get()

    if not parent_ref:
        flash("Parent profile not found.", 'error')
        return redirect(url_for('parent_dashboard'))

    parent_doc = parent_ref[0].reference  
    parent_data = parent_doc.get().to_dict()

    if not parent_data:
        flash("Parent profile not found.", 'error')
        return redirect(url_for('parent_dashboard'))

    # Get updated fields
    new_name = request.form.get('name', parent_data.get('name'))
    new_email = request.form.get('email', parent_email)
    new_children_data = request.form.getlist('children[]')  
    updated_children = parent_data.get('children', {})

    # Ensure updated_children is a dict
    if not isinstance(updated_children, dict):
        updated_children = {}

    # Handle existing children name edits
    for child_id in list(updated_children.keys()):
        updated_name = request.form.get(f'child_name_{child_id}')
        if updated_name and updated_name.strip():
            updated_children[child_id]['name'] = updated_name.strip()

    # Add new children
    for child_name in new_children_data:
        child_name = child_name.strip()
        if child_name and not any(child.get('name') == child_name for child in updated_children.values()):
            child_id = str(uuid.uuid4())
            updated_children[child_id] = {
                'name': child_name,
                'qr_code': url_for('get_qr_code', child_id=child_id, _external=True)
            }

    # Prepare updated data
    updated_data = {
        'name': new_name,
        'email': new_email,
        'children': updated_children
    }

    try:
        parent_doc.update(updated_data)
        flash("Profile updated successfully!", 'success')
    except Exception as e:
        flash(f"Error updating profile: {str(e)}", 'error')

    return redirect(url_for('parent_dashboard'))



@app.route('/log_scan', methods=['POST'])
def log_scan():
    data = request.json  
    child_id = data.get('child_id')  
    parent_email = data.get('parent_email')
    scan_time = data.get('scan_time')

    # Log the scan event under the child's entry in the parent's document
    parent_ref = db.collection('parents').document(parent_email)
    parent_ref.update({
        f'children.{child_id}.scans': firestore.ArrayUnion([{
            'scan_time': scan_time,
            'status': 'checked_in'  # or 'checked_out' based on the scan
        }])
    })
    
    # Optionally, send notification to parent via SMS
    
    return "Scan logged successfully", 200

@app.route('/delete_admin/<admin_email>', methods=['POST'])
def delete_admin(admin_email):
    """Deletes an admin. Main admin requires password confirmation."""

    if 'admin_email' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('login'))

    logged_in_admin = session['admin_email']
    password = request.form.get('password', '')  

    admin_ref = db.collection('admins').document(admin_email)
    admin_doc = admin_ref.get()

    if not admin_doc.exists:
        flash("Admin not found.", "danger")
        return redirect(url_for('admin_list'))

    admin_data = admin_doc.to_dict()

    is_main_admin = admin_data.get('is_main_admin', False)

    if is_main_admin:
        # **Only allow the main admin to delete themselves with a password**
        if logged_in_admin != admin_email:
            flash("Only the main admin can delete themselves.", "danger")
            return redirect(url_for('admin_list'))

        # **Ensure the password exists in Firestore**
        stored_password = admin_data.get('password')
        if not stored_password:
            flash("Admin account is missing password information. Contact support.", "danger")
            return redirect(url_for('admin_list'))

        # **Check password before deleting main admin**
        if not password or not check_password_hash(stored_password, password):
            flash("Incorrect password. Main admin deletion requires confirmation.", "danger")
            return redirect(url_for('admin_list'))
        
    admin_ref.delete()

    # If the main admin deletes themselves, log them out**
    if is_main_admin and logged_in_admin == admin_email:
        session.pop('admin_email', None)
        flash("Your admin account has been deleted successfully.", "success")
        return redirect(url_for('login'))

    flash("Admin deleted successfully.", "success")
    return redirect(url_for('admin_list'))




@app.route('/admin_list')
def admin_list():
    """Fetches and displays up to 5 admins."""
    if 'admin_email' not in session:
        flash("You must be logged in.", "danger")
        return redirect(url_for('login'))

    admins = db.collection('admins').limit(5).stream()

    return render_template('admin_list.html', admins=admins)



if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Fetch the port from the environment variable, or default to 5000
    port = int(os.environ.get('PORT', 5000))

    # Log the port and host for confirmation
    logging.debug(f"Starting app on http://0.0.0.0:{port}")

    serve(app, host='0.0.0.0', port=port)
