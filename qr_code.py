from flask import flash, redirect, url_for, session
import qrcode
import io
from flask import send_file
from firebase_setup import db


def generate_qr(child_id):
    # Data to encode in the QR code (example: a URL containing the child's ID)
    qr_data = f"https://your-app-url/log_scan?child_id={child_id}"
    
    # Create the QR code image
    qr = qrcode.make(qr_data)
    
    # Save the QR code image to a buffer
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    
    # Return the QR code image as a response
    return send_file(buf, mimetype='image/png')


def delete_child(child_id):
    """Deletes a child from Firestore along with their QR code."""
    if 'admin_email' not in session:  # Change from 'user_id' to 'admin_email'
        flash('You must be logged in.', 'danger')
        return redirect(url_for('login'))

    try:
        # Get all parents and check which one has this child
        parents_ref = db.collection('parents').stream()
        
        for parent in parents_ref:
            parent_data = parent.to_dict()
            parent_id = parent.id
            children = parent_data.get('children', {})

            if child_id in children:
                del children[child_id]  # Remove child from Firestore
                db.collection('parents').document(parent_id).update({'children': children})

                # Optional: Delete QR code if stored separately
                qr_ref = db.collection('qr_codes').document(child_id)
                qr_ref.delete()

                flash('Child and QR code deleted successfully!', 'success')
                break
        else:
            flash('Child not found.', 'danger')

    except Exception as e:
        flash(f'Error deleting child: {str(e)}', 'danger')

    return redirect(url_for('dashboard', admin_email=session['admin_email']))  
