"""
train_models.py  -  run this ONCE to generate the model files.

You can run it from ANY folder:
    python train_models.py
    python3 train_models.py

It will always save the models next to itself inside a 'models' sub-folder.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os
import sys

# Always work relative to THIS file's location, no matter where Python is run from
THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(THIS_DIR, 'models')
DATA_DIR   = os.path.join(THIS_DIR, 'data')

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR,   exist_ok=True)

print(f"[INFO] Saving models to: {MODELS_DIR}")
print()

# ── HELPER ────────────────────────────────────────────────────────────────────
def save(obj, filename):
    path = os.path.join(MODELS_DIR, filename)
    with open(path, 'wb') as f:
        pickle.dump(obj, f)
    print(f"  ✅ Saved: {path}")

# ═════════════════════════════════════════════════════════════════════════════
# DIABETES MODEL
# ═════════════════════════════════════════════════════════════════════════════
print("=" * 55)
print("Training Diabetes Model …")
print("=" * 55)

np.random.seed(42)
N = 2000

d = {
    'age'                    : np.random.randint(18, 80, N),
    'bmi'                    : np.random.uniform(16, 50, N),
    'blood_pressure'         : np.random.randint(55, 145, N),
    'glucose'                : np.random.randint(65, 210, N),
    'insulin'                : np.random.uniform(0, 350, N),
    'pregnancies'            : np.random.randint(0, 16, N),
    'skin_thickness'         : np.random.randint(5,  65, N),
    'diabetes_pedigree'      : np.random.uniform(0.05, 2.6, N),
    'frequent_urination'     : np.random.randint(0, 2, N),
    'excessive_thirst'       : np.random.randint(0, 2, N),
    'unexplained_weight_loss': np.random.randint(0, 2, N),
    'fatigue'                : np.random.randint(0, 2, N),
    'blurred_vision'         : np.random.randint(0, 2, N),
    'slow_healing'           : np.random.randint(0, 2, N),
    'tingling_hands_feet'    : np.random.randint(0, 2, N),
}

score = (
    (d['glucose']          > 140) * 3.0 +
    (d['bmi']              > 30)  * 2.0 +
    (d['age']              > 45)  * 1.5 +
    d['frequent_urination']       * 2.0 +
    d['excessive_thirst']         * 2.0 +
    d['unexplained_weight_loss']  * 1.5 +
    d['fatigue']                  * 1.0 +
    d['blurred_vision']           * 1.5 +
    (d['blood_pressure']   > 120) * 1.0
)
d['diagnosis'] = (score > 7).astype(int)

df  = pd.DataFrame(d)
X   = df.drop('diagnosis', axis=1)
y   = df['diagnosis']
features = list(X.columns)

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_tr)
X_te_s = scaler.transform(X_te)

model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_tr_s, y_tr)

print(f"  Train accuracy : {model.score(X_tr_s, y_tr):.3f}")
print(f"  Test  accuracy : {model.score(X_te_s, y_te):.3f}")
print(f"  Feature order  : {features}")

save(model,    'diabetes_model.pkl')
save(scaler,   'diabetes_scaler.pkl')
save(features, 'diabetes_features.pkl')
df.to_csv(os.path.join(DATA_DIR, 'diabetes_training_data.csv'), index=False)

# ═════════════════════════════════════════════════════════════════════════════
# MALARIA MODEL
# ═════════════════════════════════════════════════════════════════════════════
print()
print("=" * 55)
print("Training Malaria Model …")
print("=" * 55)

np.random.seed(43)

m = {
    'fever_days'            : np.random.randint(1, 16, N),
    'temperature'           : np.random.uniform(36.0, 41.5, N),
    'chills'                : np.random.randint(0, 2, N),
    'sweating'              : np.random.randint(0, 2, N),
    'headache_severity'     : np.random.randint(0, 11, N),
    'nausea'                : np.random.randint(0, 2, N),
    'vomiting'              : np.random.randint(0, 2, N),
    'fatigue_level'         : np.random.randint(0, 11, N),
    'muscle_pain'           : np.random.randint(0, 2, N),
    'anemia_symptoms'       : np.random.randint(0, 2, N),
    'jaundice'              : np.random.randint(0, 2, N),
    'travel_to_endemic_area': np.random.randint(0, 2, N),
    'mosquito_exposure'     : np.random.randint(0, 2, N),
    'age'                   : np.random.randint(1, 81, N),
    'cough'                 : np.random.randint(0, 2, N),
}

score = (
    (m['temperature']        > 38.5) * 3.0 +
    m['chills']                      * 2.0 +
    m['sweating']                    * 2.0 +
    (m['headache_severity']  > 6)    * 2.0 +
    m['travel_to_endemic_area']      * 3.0 +
    m['mosquito_exposure']           * 2.0 +
    (m['fever_days']         > 2)    * 1.5 +
    m['muscle_pain']                 * 1.0 +
    m['anemia_symptoms']             * 1.5 +
    m['jaundice']                    * 2.0 +
    m['nausea']                      * 1.0
)
m['diagnosis'] = (score > 8).astype(int)

df  = pd.DataFrame(m)
X   = df.drop('diagnosis', axis=1)
y   = df['diagnosis']
features = list(X.columns)

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_tr)
X_te_s = scaler.transform(X_te)

model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_tr_s, y_tr)

print(f"  Train accuracy : {model.score(X_tr_s, y_tr):.3f}")
print(f"  Test  accuracy : {model.score(X_te_s, y_te):.3f}")
print(f"  Feature order  : {features}")

save(model,    'malaria_model.pkl')
save(scaler,   'malaria_scaler.pkl')
save(features, 'malaria_features.pkl')
df.to_csv(os.path.join(DATA_DIR, 'malaria_training_data.csv'), index=False)

# ── DONE ──────────────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("✅  All models trained and saved successfully!")
print(f"📁  Location: {MODELS_DIR}")
print("=" * 55)
print()
print("You can now start app.py — the models will load correctly.")
