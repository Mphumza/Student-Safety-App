
Student Safety System 🚸👨‍👩‍👧‍👦
Overview 🌟
The Student Safety System is a cutting-edge web platform designed to ensure the safety and well-being of students. This system provides parents with the ability to manage their children's information, report incidents, and stay informed in real-time. It also empowers admins to monitor and handle incidents effectively.

With an easy-to-use interface and integrated ImgBB API for image uploads, this platform is built using modern technologies like Python, JavaScript, Flask, and Firebase Cloud for the database. The ultimate goal is to create a safe environment where communication between parents, admins, and school authorities is seamless. 🎓✨

Features 🚀
For Parents 👩‍👧‍👦:
Registration & Login: Easily create an account and log in securely. 🔐

Profile Management: Update and manage personal details and contact info. 📝

Child Management: Add, update, and deactivate child profiles whenever needed. 👶✏️

Incident Reporting: Send detailed incident reports to admins or school authorities. Includes picture uploads. 📸🛑

Image Upload via ImgBB: Effortlessly upload images for incident reports using ImgBB API. 🖼️

For Admins 🧑‍🏫:
Admin Dashboard: A powerful admin dashboard to:

View all children’s details.

View unique QR codes and QR code numbers for each child.

See parent’s name associated with the child. 🧑‍🤝‍🧑

Admin Management:

The Main Admin (first to register) cannot be deleted unless they confirm their password.

Up to 4 other admins can manage (and delete) each other.

Incident Report Inbox: Admins receive real-time notifications for incoming reports, including:

Image attachments (download or view).

Incident details (time, place, and description). 📅📍

Future Features ✨:
AI-Powered Safety Tips: Personalized safety advice for both parents and admins. 🤖💡

QR Code Scanning: A mobile app (in-production) will allow students to log in using their parent's credentials and scan QR codes. 📱🔑

Technology Stack 💻
Backend:

Python (Flask) 🐍

JavaScript 💻

Firebase Cloud Database (for storing data securely) 🔥

ImgBB API (for image uploads) 🌐

Frontend:

HTML/CSS 🖥️

JavaScript 📱

How It Works 🔧
Parent Registration: Parents sign up and create their accounts.

Adding Children: After logging in, parents can add details of their children (name, age, etc.).

Incident Reporting: Parents can send detailed reports with pictures for any incidents related to their children.

Admin Management: Admins can view children's information, manage admin roles, and monitor reports from the admin dashboard.

Notifications: Admins get notifications when new reports are sent, including images and incident details.

Mobile App: Soon, students will have access to a mobile app where they can scan QR codes to confirm their identity and safety.

Installation 📥
Requirements:
Python 3.x 🐍

Flask: Install via pip install flask

Firebase: Set up your Firebase project and use the Firebase Admin SDK.

ImgBB API: Sign up for an ImgBB API key.

Steps to Run the Project Locally:
Clone the repository:

bash
Copy
Edit
git clone https://github.com/Mphumza/Student-Safety-App.git
Install the necessary dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Set up Firebase and configure the credentials (ensure your Firebase project is linked).

Run the application:

bash
Copy
Edit
python app.py
Visit the app in your browser at http://127.0.0.1:5000/.

Usage 🛠️
Parents: Log in to manage children’s details, report incidents, and upload images.

Admins: Manage the admin panel, view incident reports, and oversee children's profiles.

Contributing 🤝
We welcome contributions! Feel free to fork the repository, open issues, or submit pull requests. Help us improve this system by adding new features, enhancing security, or fixing bugs.

License 📜
This project is licensed under the MIT License - see the LICENSE file for more information.

