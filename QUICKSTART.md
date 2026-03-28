# Quick Start Guide - DualCare Health

## ⚡ Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install flask flask-cors flask-sqlalchemy werkzeug pandas scikit-learn joblib --break-system-packages
```

### Step 2: Start the Backend
```bash
python app.py
```

You should see:
```
✅ Database initialized successfully!
✅ Default admin account created (username: admin, password: admin123)

============================================================
🏥 Health Diagnosis API Server with Authentication
============================================================
📡 Server running on: http://localhost:5000
...
```

### Step 3: Open the Frontend
Open `index.html` in your browser, or run:
```bash
python -m http.server 8000
```
Then navigate to: `http://localhost:8000`

## 🎯 First Login

### Admin Login:
- **Username**: `admin`
- **Password**: `admin123`

### Create Regular User:
1. Click "Sign up" on the login page
2. Fill in your details
3. Click "Create Account"

## 🧪 Test the System

### As a Regular User:
1. **Login** with your account
2. **Click "Diagnose"** → Select Diabetes or Malaria
3. **Fill in the form** with test values
4. **Get your diagnosis** and see recommendations
5. **Check "My History"** to see saved diagnoses
6. **Update your profile** in the Profile section

### As an Admin:
1. **Login** with admin credentials
2. **Click "Admin"** in the navigation
3. **Create a new user** using the "Create New User" button
4. **View user details** by clicking the eye icon
5. **Edit users** by clicking the edit icon
6. **Monitor statistics** on the dashboard

## 📊 Sample Test Data

### For Diabetes Test:
- Pregnancies: 2
- Glucose: 120
- Blood Pressure: 80
- Skin Thickness: 25
- Insulin: 100
- BMI: 28.5
- Diabetes Pedigree Function: 0.5
- Age: 35

### For Malaria Test:
- Temperature: 39.5
- Heart Rate: 110
- Respiratory Rate: 22
- BP Systolic: 130
- BP Diastolic: 85
- Hemoglobin: 11.5
- Check all symptom boxes for a positive test

## 🔒 Security Reminder

**IMPORTANT**: Change the default admin password immediately!

1. Login as admin
2. Go to Profile
3. Use "Change Password" section
4. Enter old password: `admin123`
5. Enter new strong password
6. Save changes

## 🆘 Common Issues

**Problem**: Can't connect to backend  
**Fix**: Make sure `python app.py` is running

**Problem**: Login not working  
**Fix**: Check browser console (F12) for errors

**Problem**: Database errors  
**Fix**: Delete `database/health_diagnosis.db` and restart

## 📁 File Checklist

Make sure you have all these files:
- ✅ app.py
- ✅ index.html
- ✅ script.js
- ✅ styles.css
- ✅ predictor.py

## 🚀 You're Ready!

Your DualCare Health with authentication and admin panel is now running!

For detailed information, see the full README.md file.
