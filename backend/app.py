from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import sys, os, hashlib, time

# ── PATH SETUP ──────────────────────────────────────────────────────────────
BACKEND_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR   = os.path.dirname(BACKEND_DIR)
ML_MODELS_DIR = os.path.join(PROJECT_DIR, 'ml-models')
sys.path.insert(0, ML_MODELS_DIR)

print(f"[INFO] Backend  : {BACKEND_DIR}")
print(f"[INFO] ML Models: {ML_MODELS_DIR}")
print(f"[INFO] predictor.py found: {os.path.exists(os.path.join(ML_MODELS_DIR, 'predictor.py'))}")

from predictor import HealthPredictor

# ── APP SETUP ────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "https://fidamian01.github.io"
]}})   # no credentials=True needed
app.config["SECRET_KEY"] = "healthai-token-secret-2024"

DATABASE_DIR  = os.path.join(PROJECT_DIR, 'database')
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(DATABASE_DIR, 'health_diagnosis.db')
app.config['SQLALCHEMY_DATABASE_URI']  = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

MODELS_DIR = os.path.join(ML_MODELS_DIR, 'models')
predictor  = HealthPredictor(model_dir=MODELS_DIR)

# ── TOKEN STORE ──────────────────────────────────────────────────────────────
# Simple in-memory token store.  Token is sent in the Authorization header,
# so it works with any origin and never touches cookies.
active_tokens = {}  # token_string -> user_id

def generate_token(user_id):
    raw   = f"{user_id}:{app.config['SECRET_KEY']}:{time.time()}"
    token = hashlib.sha256(raw.encode()).hexdigest()
    active_tokens[token] = user_id
    return token

def get_user_id_from_request():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None
    return active_tokens.get(auth[len('Bearer '):])

# ── MODELS ───────────────────────────────────────────────────────────────────
class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    full_name     = db.Column(db.String(100), nullable=False)
    phone         = db.Column(db.String(20))
    age           = db.Column(db.Integer)
    gender        = db.Column(db.String(10))
    is_admin      = db.Column(db.Boolean, default=False)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)
    diagnoses     = db.relationship('Diagnosis', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, p):  self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)

    def to_dict(self):
        return {
            'id': self.id, 'username': self.username, 'email': self.email,
            'full_name': self.full_name, 'phone': self.phone, 'age': self.age,
            'gender': self.gender, 'is_admin': self.is_admin, 'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

class Diagnosis(db.Model):
    id                    = db.Column(db.Integer, primary_key=True)
    user_id               = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease               = db.Column(db.String(50),  nullable=False)
    symptoms              = db.Column(db.JSON,        nullable=False)
    prediction            = db.Column(db.Integer)
    probability           = db.Column(db.Float)
    severity              = db.Column(db.String(20))
    recommendations       = db.Column(db.JSON)
    seek_medical_attention= db.Column(db.Boolean)
    created_at            = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'disease': self.disease,
            'symptoms': self.symptoms, 'prediction': self.prediction,
            'probability': self.probability, 'severity': self.severity,
            'recommendations': self.recommendations,
            'seek_medical_attention': self.seek_medical_attention,
            'created_at': self.created_at.isoformat(),
        }

# ── DECORATORS ───────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_user_id_from_request():
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        uid = get_user_id_from_request()
        if not uid:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.get(uid)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated

# ── AUTH ROUTES ───────────────────────────────────────────────────────────────
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        for f in ['username','password','email','full_name']:
            if not data.get(f): return jsonify({'error': f'{f} is required'}), 400
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        user = User(username=data['username'], email=data['email'],
                    full_name=data['full_name'], phone=data.get('phone'),
                    age=data.get('age'), gender=data.get('gender'), is_admin=False)
        user.set_password(data['password'])
        user.last_login = datetime.utcnow()
        db.session.add(user); db.session.commit()
        token = generate_token(user.id)
        return jsonify({'message': 'Account created', 'token': token, 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data.get('username','')).first()
        if not user or not user.check_password(data.get('password','')):
            return jsonify({'error': 'Invalid username or password'}), 401
        if not user.is_active:
            return jsonify({'error': 'Account deactivated. Contact admin.'}), 403
        user.last_login = datetime.utcnow(); db.session.commit()
        token = generate_token(user.id)
        print(f"[LOGIN] {user.username}  admin={user.is_admin}  token={token[:12]}...")
        return jsonify({'message': 'Login successful', 'token': token, 'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    auth = request.headers.get('Authorization','')
    if auth.startswith('Bearer '):
        active_tokens.pop(auth[len('Bearer '):], None)
    return jsonify({'message': 'Logged out'}), 200

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    uid = get_user_id_from_request()
    if not uid: return jsonify({'logged_in': False}), 200
    user = User.query.get(uid)
    if not user or not user.is_active: return jsonify({'logged_in': False}), 200
    return jsonify({'logged_in': True, 'user': user.to_dict()}), 200

# ── PROFILE ROUTES ────────────────────────────────────────────────────────────
@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        user = User.query.get(get_user_id_from_request())
        data = request.get_json()
        for field in ['full_name','phone','age','gender']:
            if field in data: setattr(user, field, data[field])
        if 'email' in data:
            ex = User.query.filter_by(email=data['email']).first()
            if ex and ex.id != user.id: return jsonify({'error': 'Email in use'}), 400
            user.email = data['email']
        db.session.commit()
        return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

@app.route('/api/profile/password', methods=['PUT'])
@login_required
def change_password():
    try:
        user = User.query.get(get_user_id_from_request())
        data = request.get_json()
        if not user.check_password(data.get('old_password','')):
            return jsonify({'error': 'Current password is incorrect'}), 401
        new_pw = data.get('new_password','')
        if len(new_pw) < 6: return jsonify({'error': 'Password must be at least 6 characters'}), 400
        user.set_password(new_pw); db.session.commit()
        return jsonify({'message': 'Password changed'}), 200
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

# ── DIAGNOSIS ROUTES ──────────────────────────────────────────────────────────
@app.route('/api/predict/diabetes', methods=['POST'])
@login_required
def predict_diabetes():
    try:
        uid = get_user_id_from_request()
        symptoms = request.get_json().get('symptoms')
        if not symptoms: return jsonify({'error': 'Symptoms required'}), 400
        result = predictor.predict_diabetes(symptoms)
        if 'error' in result: return jsonify({'error': result['error']}), 400
        diag = Diagnosis(user_id=uid, disease='diabetes', symptoms=symptoms,
                         prediction=result['prediction'], probability=result['probability'],
                         severity=result['severity'], recommendations=result['recommendations'],
                         seek_medical_attention=result['seek_medical_attention'])
        db.session.add(diag); db.session.commit()
        result['diagnosis_id'] = diag.id
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

@app.route('/api/predict/malaria', methods=['POST'])
@login_required
def predict_malaria():
    try:
        uid = get_user_id_from_request()
        symptoms = request.get_json().get('symptoms')
        if not symptoms: return jsonify({'error': 'Symptoms required'}), 400
        result = predictor.predict_malaria(symptoms)
        if 'error' in result: return jsonify({'error': result['error']}), 400
        diag = Diagnosis(user_id=uid, disease='malaria', symptoms=symptoms,
                         prediction=result['prediction'], probability=result['probability'],
                         severity=result['severity'], recommendations=result['recommendations'],
                         seek_medical_attention=result['seek_medical_attention'])
        db.session.add(diag); db.session.commit()
        result['diagnosis_id'] = diag.id
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

@app.route('/api/diagnoses/my-history', methods=['GET'])
@login_required
def get_my_diagnoses():
    uid = get_user_id_from_request()
    diagnoses = Diagnosis.query.filter_by(user_id=uid).order_by(Diagnosis.created_at.desc()).all()
    return jsonify([d.to_dict() for d in diagnoses])

# ── ADMIN ROUTES ──────────────────────────────────────────────────────────────
@app.route('/api/admin/statistics', methods=['GET'])
@admin_required
def admin_statistics():
    return jsonify({
        'total_users':       User.query.filter_by(is_admin=False).count(),
        'active_users':      User.query.filter_by(is_admin=False, is_active=True).count(),
        'inactive_users':    User.query.filter_by(is_admin=False, is_active=False).count(),
        'total_diagnoses':   Diagnosis.query.count(),
        'diabetes_positive': Diagnosis.query.filter_by(disease='diabetes', prediction=1).count(),
        'malaria_positive':  Diagnosis.query.filter_by(disease='malaria',  prediction=1).count(),
        'diabetes_total':    Diagnosis.query.filter_by(disease='diabetes').count(),
        'malaria_total':     Diagnosis.query.filter_by(disease='malaria').count(),
    })

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    users = User.query.all()
    result = []
    for u in users:
        d = u.to_dict()
        d['diagnosis_count'] = Diagnosis.query.filter_by(user_id=u.id).count()
        result.append(d)
    return jsonify(result)

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def admin_create_user():
    try:
        data = request.get_json()
        for f in ['username','password','email','full_name']:
            if not data.get(f): return jsonify({'error': f'{f} is required'}), 400
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        user = User(username=data['username'], email=data['email'],
                    full_name=data['full_name'], phone=data.get('phone'),
                    age=data.get('age'), gender=data.get('gender'),
                    is_admin=data.get('is_admin', False))
        user.set_password(data['password'])
        db.session.add(user); db.session.commit()
        return jsonify({'message': 'User created', 'user': user.to_dict()}), 201
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def admin_get_user(user_id):
    return jsonify(User.query.get_or_404(user_id).to_dict())

@app.route('/api/admin/users/<int:user_id>/diagnoses', methods=['GET'])
@admin_required
def admin_get_user_diagnoses(user_id):
    user = User.query.get_or_404(user_id)
    diagnoses = Diagnosis.query.filter_by(user_id=user_id).order_by(Diagnosis.created_at.desc()).all()
    return jsonify({'user': user.to_dict(), 'diagnoses': [d.to_dict() for d in diagnoses]})

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def admin_update_user(user_id):
    try:
        me   = User.query.get(get_user_id_from_request())
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        if user_id == me.id and data.get('is_active') == False:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        for field in ['full_name','phone','age','gender','is_active']:
            if field in data: setattr(user, field, data[field])
        if 'username' in data:
            ex = User.query.filter_by(username=data['username']).first()
            if ex and ex.id != user.id: return jsonify({'error': 'Username taken'}), 400
            user.username = data['username']
        if 'email' in data:
            ex = User.query.filter_by(email=data['email']).first()
            if ex and ex.id != user.id: return jsonify({'error': 'Email taken'}), 400
            user.email = data['email']
        if 'is_admin' in data and user_id != me.id:
            user.is_admin = data['is_admin']
        db.session.commit()
        return jsonify({'message': 'User updated', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    try:
        if user_id == get_user_id_from_request():
            return jsonify({'error': 'Cannot delete your own account'}), 400
        user = User.query.get_or_404(user_id)
        db.session.delete(user); db.session.commit()
        return jsonify({'message': 'User deleted'}), 200
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def admin_reset_password(user_id):
    try:
        user   = User.query.get_or_404(user_id)
        new_pw = request.get_json().get('new_password','')
        if len(new_pw) < 6: return jsonify({'error': 'Min 6 characters'}), 400
        user.set_password(new_pw); db.session.commit()
        return jsonify({'message': 'Password reset'}), 200
    except Exception as e:
        db.session.rollback(); return jsonify({'error': str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# ── STARTUP ───────────────────────────────────────────────────────────────────
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@healthai.com',
                         full_name='System Administrator', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin); db.session.commit()
            print("✅ Default admin created  →  username: admin  |  password: admin123")
        print("✅ Database ready")

if __name__ == '__main__':
    init_db()
    print("\n" + "="*55)
    print("🏥  HealthAI Diagnosis API  —  Token Auth Mode")
    print("="*55)
    print("📡  http://localhost:5000")
    print("🔐  Admin login: admin / admin123")
    print("="*55 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
