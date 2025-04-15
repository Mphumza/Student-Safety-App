# 🚸 Student Safety System Web App

The **Student Safety System** is a modern web platform designed to enhance the **safety and transparency** of students' daily activities. It provides a **secure environment for parents and school authorities** to communicate, report incidents, and track students in real-time.

Built with Python, Flask, Firebase, and JavaScript, this system empowers **parents** to manage their children's profiles and report incidents, while giving **admins** a robust dashboard for monitoring safety-related events.

---

## 🌟 Features

### 👩‍👧‍👦 For Parents

- **🔐 Registration & Login**  
  Secure account creation and login.

- **📝 Profile Management**  
  Update personal and contact details with ease.

- **👶 Child Management**  
  Add, update, or deactivate child profiles.

- **📸 Incident Reporting**  
  Send detailed incident reports to school admins, including:
  - Time
  - Location
  - Description
  - Image attachment (via **ImgBB API**)

- **🖼️ Image Upload via ImgBB**  
  Parents can upload supporting images to enhance their reports.

---

### 🧑‍🏫 For Admins

- **📊 Admin Dashboard**  
  A control center to:
  - View all children's details
  - View and manage parent-child associations
  - Access each child’s unique **QR code** and **UUID**
  - Track and manage all incident reports

- **👥 Admin Role Management**
  - First registered user becomes **Main Admin**
  - Main Admin cannot be deleted unless password is confirmed
  - Up to 4 other admins can be created and managed

- **📥 Real-time Report Inbox**
  - Live notifications for each incident
  - View/download images, description, timestamp, and more

---

## 📱 Mobile App (Companion)

> 🚧 The mobile app is **under development** and is **not included in this repository**.

**Target Users**: Students and school gate officials  
**Purpose**: Acts as a digital scanner to interact with the web system

### How It Works:

- Each child’s **QR code**, along with their name, parent’s name, and UUID, is generated and visible from the **web dashboard**.
- **School officials (using the mobile app)** scan the QR codes:
  - **At the gate or entrance** in the morning and afternoon
  - The system records time of entry/exit
  - **Instant notification** is sent to the parent for confirmation
- App authenticates using **parent credentials**

---

## 🛣️ Roadmap

- [x] Firebase Authentication  
- [x] Parent & Admin Dashboards  
- [x] Incident Reporting with Image Upload  
- [x] QR Code Generation per Child  
- [ ] QR Code Scanning Integration (via Mobile App)  
- [ ] Parent Notification via SMS/Email  
- [ ] AI Safety Tips Panel  
- [ ] Multi-student support per parent account  

---

## 💡 Vision

To **bridge communication gaps** between schools and parents by making student movements **transparent, trackable, and secure in real-time**.

By blending **smart technology** with **intuitive usability**, we aim to offer peace of mind to thousands of families and enhance student safety across schools.

---

## ⚙️ Tech Stack

### Backend:
- Python (Flask) 🐍  
- Firebase Cloud Firestore 🔥  
- ImgBB API (for image uploads) 🌐  

### Frontend:
- HTML/CSS 🎨  
- JavaScript 📱  

---

## 🔧 Installation & Setup

### 📋 Requirements:
- Python 3.x  
- Flask (`pip install flask`)  
- Firebase Admin SDK (with credentials)  
- ImgBB API Key  

### 🛠️ Steps:

1. **Clone the repository**  
```bash
git clone https://github.com/Mphumza/Student-Safety-App.git
```

2. **Install dependencies**  
```bash
pip install -r requirements.txt
```

3. **Set up Firebase**
- Create a Firebase project  
- Download your Admin SDK JSON  
- Link and configure it within your Flask project  

4. **Run the app**  
```bash
python app.py
```

5. **Access in browser**  
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📬 Contact

For feature requests, bug reports, or collaborations:  
📧 mphumelelingema@icloud.com

---

## 🤝 Contributing

We welcome contributions!  
If you're passionate about **EdTech**, **student safety**, or improving community-driven apps, feel free to:

- Fork the repo  
- Submit pull requests  
- Open issues  

---

## 🏷️ Tags

`#Flask` `#Firebase` `#StudentSafety` `#QRcodes` `#ImgBB` `#WebApp` `#EdTech` `#ParentCommunication`

---

## ⭐ Give It a Star!

If you believe in safer schools through technology, please **star this repository** to show your support!

