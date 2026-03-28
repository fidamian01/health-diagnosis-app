# DualCare Health - Updated with Authentication & Admin Panel

## 🎉 New Features Added

### 1. **User Authentication System**
- **Login Page**: Secure user login with username and password
- **Signup Page**: New user registration with profile information
- **Session Management**: Automatic session handling with cookies
- **Password Security**: Passwords are hashed using Werkzeug's security functions

### 2. **Per-User Diagnosis Storage**
- Each user has their own private diagnosis history
- Users can only see their own diagnoses
- Complete data isolation between users
- Diagnosis history accessible from "My History" section

### 3. **Admin Panel**
- **Separate Admin Login**: Admins use the same login page but get access to admin features
- **User Management Dashboard**: View all registered users
- **Monitor User Activity**: See diagnosis counts per user
- **Create Users**: Admins can create new user accounts
- **Edit Users**: Update user information and status
- **Delete Users**: Remove user accounts (with confirmation)
- **View User Details**: See complete user profile and diagnosis history
- **Statistics Dashboard**: Overview of total users, diagnoses, and cases

## 🔐 Default Admin Account

**Username**: `admin`  
**Password**: `admin123`

⚠️ **IMPORTANT**: Change the admin password immediately after first login!

## 📋 Features Overview

### For Regular Users:
- ✅ Signup/Login authentication
- ✅ Personal profile management
- ✅ Password change functionality
- ✅ Diabetes diagnosis prediction
- ✅ Malaria diagnosis prediction
- ✅ View personal diagnosis history
- ✅ Secure data storage

### For Administrators:
- ✅ All regular user features
- ✅ View all registered users
- ✅ Create new user accounts
- ✅ Edit user information
- ✅ Delete user accounts
- ✅ View user diagnosis history
- ✅ Monitor system statistics
- ✅ Reset user passwords
- ✅ Activate/Deactivate user accounts

## 🚀 Setup Instructions

### Prerequisites
```bash
pip install flask flask-cors flask-sqlalchemy werkzeug pandas scikit-learn joblib --break-system-packages
```

### File Structure
```
health-diagnosis-app/
├── app.py              # Backend with authentication
├── index.html          # Frontend with login/signup/admin
├── script.js           # JavaScript with auth handling
├── styles.css          # Styling (from original)
├── predictor.py        # ML predictor (from original)
└── database/
    └── health_diagnosis.db  # SQLite database (auto-created)
```

### Running the Application

1. **Start the Backend Server**:
```bash
python app.py
```

The server will start on `http://localhost:5000`

2. **Open the Frontend**:
Open `index.html` in your web browser, or serve it using:
```bash
python -m http.server 8000
```
Then navigate to `http://localhost:8000`

3. **First Time Setup**:
- The database will be automatically created
- A default admin account will be created
- Login with admin credentials (admin/admin123)
- Change the admin password immediately

## 📱 How to Use

### For New Users:
1. Click on the "Sign up" link on the login page
2. Fill in your details (username, email, password, name)
3. Click "Create Account"
4. You'll be automatically logged in

### For Existing Users:
1. Enter your username and password
2. Click "Login"
3. Access your dashboard

### Getting a Diagnosis:
1. Click "Diagnose" in the navigation
2. Select either Diabetes or Malaria
3. Fill in the required symptoms/measurements
4. Click "Get Diagnosis"
5. View your results and recommendations
6. Check "My History" to see all past diagnoses

### For Admins:
1. Login with admin credentials
2. Click "Admin" in the navigation menu
3. View statistics dashboard
4. Manage users:
   - Click "View" to see user details and diagnosis history
   - Click "Edit" to modify user information
   - Click "Delete" to remove a user
   - Click "Create New User" to add users manually

## 🔒 Security Features

1. **Password Hashing**: All passwords are hashed using Werkzeug's security functions
2. **Session Management**: Secure session cookies with secret key
3. **CSRF Protection**: Built-in Flask session protection
4. **Data Isolation**: Users can only access their own data
5. **Admin Authorization**: Admin-only routes protected with decorators
6. **Input Validation**: All user inputs are validated before processing

## 🗄️ Database Schema

### User Table:
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password
- `email`: Unique email address
- `full_name`: User's full name
- `phone`: Phone number (optional)
- `age`: Age (optional)
- `gender`: Gender (optional)
- `is_admin`: Admin flag
- `is_active`: Account status
- `created_at`: Registration date
- `last_login`: Last login timestamp

### Diagnosis Table:
- `id`: Primary key
- `user_id`: Foreign key to User
- `disease`: Disease type (diabetes/malaria)
- `symptoms`: JSON of symptoms
- `prediction`: 0 or 1
- `probability`: Confidence score
- `severity`: Severity level
- `recommendations`: JSON of recommendations
- `seek_medical_attention`: Boolean flag
- `created_at`: Diagnosis timestamp

## 🔧 API Endpoints

### Authentication:
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/check` - Check authentication status

### User Profile:
- `PUT /api/profile` - Update profile
- `PUT /api/profile/password` - Change password

### Diagnosis:
- `POST /api/predict/diabetes` - Diabetes prediction
- `POST /api/predict/malaria` - Malaria prediction
- `GET /api/diagnoses/my-history` - Get user's diagnosis history

### Admin Only:
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/<id>` - Get user details
- `GET /api/admin/users/<id>/diagnoses` - Get user diagnoses
- `POST /api/admin/users` - Create new user
- `PUT /api/admin/users/<id>` - Update user
- `DELETE /api/admin/users/<id>` - Delete user
- `POST /api/admin/users/<id>/reset-password` - Reset user password
- `GET /api/admin/statistics` - Get system statistics

## 🎨 UI Sections

1. **Login Page**: Authentication for existing users
2. **Signup Page**: Registration for new users
3. **Home Dashboard**: Welcome page with quick stats
4. **Diagnose**: Disease selection and diagnosis forms
5. **My History**: Personal diagnosis history
6. **Profile**: User profile management and password change
7. **Admin Panel**: User management and system monitoring (admin only)

## 📝 Important Notes

1. **Production Deployment**:
   - Change the default admin password
   - Use a strong SECRET_KEY
   - Enable HTTPS (set SESSION_COOKIE_SECURE to True)
   - Use a production-grade database (PostgreSQL/MySQL)
   - Add rate limiting
   - Implement proper logging

2. **Database Location**:
   - The SQLite database will be created in `../database/health_diagnosis.db`
   - Make sure the directory exists or the app will create it

3. **ML Models**:
   - Ensure the ML models are in `../ml-models/models/` directory
   - Models should be named: `diabetes_model.pkl` and `malaria_model.pkl`

## 🐛 Troubleshooting

**Issue**: Can't login  
**Solution**: Ensure the backend server is running and check browser console for errors

**Issue**: Database errors  
**Solution**: Delete the database file and restart the app to recreate it

**Issue**: Admin features not showing  
**Solution**: Ensure you're logged in with an admin account

**Issue**: CORS errors  
**Solution**: Ensure backend is running on port 5000 and CORS is properly configured

## 📞 Support

For issues or questions:
1. Check the browser console for JavaScript errors
2. Check the Flask console for backend errors
3. Verify all required files are in the correct locations
4. Ensure all dependencies are installed

## 🔄 Updates from Original Version

### Backend Changes (app.py):
- Added User model with authentication
- Removed Patient model (merged into User)
- Changed Diagnosis to link to User instead of Patient
- Added authentication decorators (@login_required, @admin_required)
- Added session management
- Added all authentication routes
- Added admin management routes
- Added password hashing and verification

### Frontend Changes (index.html):
- Added login page
- Added signup page
- Added profile management section
- Added admin panel
- Modified navigation to include logout
- Added modals for user management
- Updated all sections to work with authentication

### JavaScript Changes (script.js):
- Added authentication functions
- Added session checking
- Added profile management
- Added admin functions
- Updated all API calls to include credentials
- Added modal handling for admin features

## 🎯 Next Steps

1. Change the default admin password
2. Test the signup/login flow
3. Create some test diagnoses
4. Explore the admin panel
5. Customize styling if needed
6. Deploy to production server

Enjoy your upgraded DualCare Health! 🏥
