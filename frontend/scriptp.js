// ── CONFIG ────────────────────────────────────────────────────────────────────
const API_BASE = 'https://health-diagnosis-backend-b8dl.onrender.com';

// ── TOKEN HELPERS ─────────────────────────────────────────────────────────────
// Store token in localStorage so it persists and is sent on every request.
// This completely avoids cookie/CORS/SameSite issues.

function saveToken(token) { localStorage.setItem('auth_token', token); }
function getToken()       { return localStorage.getItem('auth_token'); }
function clearToken()     { localStorage.removeItem('auth_token'); localStorage.removeItem('current_user'); }
function saveUser(user)   { localStorage.setItem('current_user', JSON.stringify(user)); }
function loadUser()       { const u = localStorage.getItem('current_user'); return u ? JSON.parse(u) : null; }

// Every API call goes through this — automatically attaches the token
async function api(path, options = {}) {
    const token = getToken();
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
    const data = await response.json();
    return { ok: response.ok, status: response.status, data };
}

// ── STATE ─────────────────────────────────────────────────────────────────────
let currentUser   = null;
let currentDisease = null;

// ── BOOT ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();

    // If we have a token saved, verify it is still valid
    if (getToken()) {
        const { ok, data } = await api('/auth/check');
        if (ok && data.logged_in) {
            currentUser = data.user;
            saveUser(currentUser);
            showMainApp();
            return;
        }
    }
    // No valid token — show login
    clearToken();
    showLogin();
});

// ── AUTH DISPLAY ──────────────────────────────────────────────────────────────
function showLogin() {
    document.getElementById('loginPage').style.display  = 'flex';
    document.getElementById('signupPage').style.display = 'none';
    document.getElementById('mainApp').style.display    = 'none';
    const err = document.getElementById('loginError');
    if (err) { err.style.display = 'none'; err.textContent = ''; }
}

function showSignup() {
    document.getElementById('loginPage').style.display  = 'none';
    document.getElementById('signupPage').style.display = 'flex';
    document.getElementById('mainApp').style.display    = 'none';
}

function showMainApp() {
    document.getElementById('loginPage').style.display  = 'none';
    document.getElementById('signupPage').style.display = 'none';
    document.getElementById('mainApp').style.display    = 'block';

    document.getElementById('userInfo').innerHTML =
        `<i class="fas fa-user-circle"></i> ${currentUser.full_name}`;

    document.getElementById('adminNavItem').style.display =
        currentUser.is_admin ? 'block' : 'none';

    loadMyDiagnosesCount();
    showSection('home');
}

// ── EVENT LISTENERS ───────────────────────────────────────────────────────────
function setupEventListeners() {
    document.getElementById('loginForm')   .addEventListener('submit', e => { e.preventDefault(); handleLogin(); });
    document.getElementById('signupForm')  .addEventListener('submit', e => { e.preventDefault(); handleSignup(); });
    document.getElementById('profileForm') .addEventListener('submit', e => { e.preventDefault(); handleProfileUpdate(); });
    document.getElementById('passwordForm').addEventListener('submit', e => { e.preventDefault(); handlePasswordChange(); });
    document.getElementById('diabetesForm').addEventListener('submit', e => { e.preventDefault(); handleDiabetesPrediction(); });
    document.getElementById('malariaForm') .addEventListener('submit', e => { e.preventDefault(); handleMalariaPrediction(); });
    document.getElementById('editUserForm')  .addEventListener('submit', e => { e.preventDefault(); handleUpdateUser(); });
    document.getElementById('createUserForm').addEventListener('submit', e => { e.preventDefault(); handleCreateUser(); });
}

// ── LOGIN ─────────────────────────────────────────────────────────────────────
async function handleLogin() {
    const errorDiv = document.getElementById('loginError');
    errorDiv.style.display = 'none';

    const { ok, data } = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
            username: document.getElementById('loginUsername').value,
            password: document.getElementById('loginPassword').value,
        })
    });

    if (ok) {
        saveToken(data.token);
        currentUser = data.user;
        saveUser(currentUser);
        showMainApp();
    } else {
        errorDiv.textContent  = data.error || 'Login failed';
        errorDiv.style.display = 'block';
    }
}

// ── SIGNUP ────────────────────────────────────────────────────────────────────
async function handleSignup() {
    const errorDiv = document.getElementById('signupError');
    errorDiv.style.display = 'none';

    const { ok, data } = await api('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({
            username  : document.getElementById('signupUsername').value,
            password  : document.getElementById('signupPassword').value,
            email     : document.getElementById('signupEmail').value,
            full_name : document.getElementById('signupFullName').value,
            age       : document.getElementById('signupAge').value    || null,
            gender    : document.getElementById('signupGender').value || null,
            phone     : document.getElementById('signupPhone').value  || null,
        })
    });

    if (ok) {
        saveToken(data.token);
        currentUser = data.user;
        saveUser(currentUser);
        showMainApp();
    } else {
        errorDiv.textContent  = data.error || 'Signup failed';
        errorDiv.style.display = 'block';
    }
}

// ── LOGOUT ────────────────────────────────────────────────────────────────────
async function logout() {
    await api('/auth/logout', { method: 'POST' });
    clearToken();
    currentUser = null;
    showLogin();
}

// ── NAVIGATION ────────────────────────────────────────────────────────────────
function showSection(name) {
    ['home','diagnose','diagnosisForm','results','history','profile','admin']
        .forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });

    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

    const target = document.getElementById(name);
    if (target) target.style.display = 'block';

    const link = document.querySelector(`.nav-link[onclick*="${name}"]`);
    if (link) link.classList.add('active');

    if (name === 'history') loadMyHistory();
    if (name === 'profile') loadProfile();
    if (name === 'admin' && currentUser?.is_admin) loadAdminDashboard();
}

// ── DISEASE SELECTION ─────────────────────────────────────────────────────────
function selectDisease(disease) {
    currentDisease = disease;
    document.getElementById('diagnose').style.display      = 'none';
    document.getElementById('diagnosisForm').style.display = 'block';

    document.getElementById('diseaseTitle').textContent =
        disease.charAt(0).toUpperCase() + disease.slice(1) + ' Diagnosis';

    document.getElementById('diabetesForm').style.display = disease === 'diabetes' ? 'block' : 'none';
    document.getElementById('malariaForm') .style.display = disease === 'malaria'  ? 'block' : 'none';
}

// ── DIAGNOSIS ─────────────────────────────────────────────────────────────────

// ── BMI CALCULATOR ────────────────────────────────────────────────────────────
function calcBMI() {
    const weight   = parseFloat(document.getElementById('bmiWeight').value);
    const heightCm = parseFloat(document.getElementById('bmiHeight').value);
    const display  = document.getElementById('bmiDisplay');
    const category = document.getElementById('bmiCategory');
    const hidden   = document.getElementById('bmiHiddenValue');
    const row      = document.getElementById('bmiResultRow');

    if (!weight || !heightCm || heightCm < 50) {
        if (row) row.style.display = 'none';
        if (hidden) hidden.value = '';
        return;
    }

    const bmi     = weight / Math.pow(heightCm / 100, 2);
    const rounded = bmi.toFixed(1);
    if (hidden) hidden.value = rounded;

    let label, color;
    if      (bmi < 18.5) { label = 'Underweight';  color = '#4f8ef7'; }
    else if (bmi < 25)   { label = 'Healthy weight'; color = '#3fb950'; }
    else if (bmi < 30)   { label = 'Overweight';    color = '#d29922'; }
    else if (bmi < 35)   { label = 'Obese';         color = '#f85149'; }
    else                 { label = 'Severely obese'; color = '#f85149'; }

    if (display)  { display.textContent = `BMI ${rounded}`; display.style.color = color; }
    if (category) { category.textContent = label + (bmi >= 25 ? ' — raised diabetes risk' : ' — weight in healthy range'); }
    if (row)      row.style.display = 'flex';
}

async function handleDiabetesPrediction() {
    const fd = new FormData(document.getElementById('diabetesForm'));

    // Age is required; read it directly
    const age = parseFloat(fd.get('Age'));

    // BMI — calculated by the inline calculator; stored in hidden field
    const bmiVal = fd.get('BMI');
    if (bmiVal && parseFloat(bmiVal) > 0) {
        // Store on window so displayResults can show a BMI note
        window._lastBMI = parseFloat(bmiVal);
    } else {
        window._lastBMI = null;
    }

    // Blood sugar readings — use population average if not provided
    const FFPG_raw = fd.get('FFPG');
    const FPG_raw  = fd.get('FPG');
    const FFPG = FFPG_raw && FFPG_raw !== '' ? parseFloat(FFPG_raw) : 173;
    // If only one reading given, mirror it for the second; otherwise use dataset average
    const FPG  = FPG_raw  && FPG_raw  !== '' ? parseFloat(FPG_raw)  : (FFPG_raw && FFPG_raw !== '' ? FFPG : 161);

    // Cholesterol — use healthy-population medians if not provided
    const HDL_raw = fd.get('HDL');
    const LDL_raw = fd.get('LDL');
    const HDL = HDL_raw && HDL_raw !== '' ? parseFloat(HDL_raw) : 52;
    const LDL = LDL_raw && LDL_raw !== '' ? parseFloat(LDL_raw) : 110;

    // Blood pressure — use normal baseline if not provided
    const SBP_raw = fd.get('SBP');
    const SBP = SBP_raw && SBP_raw !== '' ? parseFloat(SBP_raw) : 120;

    await makePrediction('diabetes', {
        FFPG            : FFPG,
        FPG             : FPG,
        Age             : age,
        HDL             : HDL,
        LDL             : LDL,
        'Family History': fd.get('Family History') ? 1 : 0,
        SBP             : SBP,
    });
}

async function handleMalariaPrediction() {
    const fd = new FormData(document.getElementById('malariaForm'));

    // Optional lab fields — fill with dataset medians if left blank
    const parasiteRaw  = fd.get('Parasite Density');
    const hemoglobinRaw = fd.get('Hemoglobin');
    const wbcRaw       = fd.get('WBC Count');
    const feverDaysRaw = fd.get('Fever Duration');

    const parasiteDensity = parasiteRaw   && parasiteRaw   !== '' ? parseFloat(parasiteRaw)   : 25067; // dataset median
    const hemoglobin      = hemoglobinRaw && hemoglobinRaw !== '' ? parseFloat(hemoglobinRaw) : 12.0;  // healthy midpoint
    const wbcCount        = wbcRaw        && wbcRaw        !== '' ? parseFloat(wbcRaw)        : 8.0;   // normal midpoint
    const feverDays       = feverDaysRaw  && feverDaysRaw  !== '' ? parseFloat(feverDaysRaw)  : 3;     // common presentation

    await makePrediction('malaria', {
        Age               : parseFloat(fd.get('Age')),
        Temperature       : parseFloat(fd.get('Temperature')),
        'Fever Duration'  : feverDays,
        'Parasite Density': parasiteDensity,
        Hemoglobin        : hemoglobin,
        'WBC Count'       : wbcCount,
        Chills            : fd.get('Chills')          ? 1 : 0,
        Sweating          : fd.get('Sweating')        ? 1 : 0,
        Headache          : fd.get('Headache')        ? 1 : 0,
        'Travel History'  : fd.get('Travel History')  ? 1 : 0,
        'Previous Malaria': fd.get('Previous Malaria') ? 1 : 0,
    });
}

async function makePrediction(disease, symptoms) {
    const { ok, data } = await api(`/predict/${disease}`, {
        method: 'POST',
        body  : JSON.stringify({ symptoms })
    });
    if (ok) displayResults(data, disease);
    else    alert(data.error || 'Prediction failed');
}

function displayResults(data, disease) {
    // If the API returned an error, show it clearly
    if (data.error) {
        document.getElementById('resultContent').innerHTML =
            `<div style="background:#fee;color:#c33;padding:20px;border-radius:10px;margin:20px 0;">
                <h3>⚠️ Prediction Error</h3>
                <p>${data.error}</p>
                <p style="margin-top:10px;font-size:13px;">Please check all fields are filled in correctly and try again.</p>
             </div>`;
        document.getElementById('diagnosisForm').style.display = 'none';
        document.getElementById('results').style.display       = 'block';
        return;
    }

    const positive = data.prediction === 1;
    const pct      = typeof data.probability === 'number' ? data.probability.toFixed(2) : '–';

    // Result label helpers
    function diabetesResultLabel(positive, severity) {
        if (!positive)               return { headline: 'Low Risk of Diabetes',            accent: '#3fb950', bg: 'rgba(63,185,80,0.08)',   border: 'rgba(63,185,80,0.25)' };
        if (severity === 'low')      return { headline: 'Slightly Elevated Risk',          accent: '#d29922', bg: 'rgba(210,153,34,0.08)',  border: 'rgba(210,153,34,0.25)' };
        if (severity === 'moderate') return { headline: 'Moderate Risk — See a Doctor',   accent: '#d29922', bg: 'rgba(210,153,34,0.08)',  border: 'rgba(210,153,34,0.25)' };
        if (severity === 'high')     return { headline: 'High Risk — Please See a Doctor', accent: '#f85149', bg: 'rgba(248,81,73,0.08)',   border: 'rgba(248,81,73,0.25)' };
        return                              { headline: 'Very High Risk — Seek Care Today', accent: '#f85149', bg: 'rgba(248,81,73,0.1)',    border: 'rgba(248,81,73,0.4)' };
    }

    function riskMeter(pct) {
        const fill  = Math.min(100, parseFloat(pct) || 0);
        const color = fill < 30 ? '#3fb950' : fill < 60 ? '#d29922' : fill < 80 ? '#f85149' : '#f85149';
        return `
            <div style="margin:20px 0 4px;">
                <div style="display:flex;justify-content:space-between;font-size:11px;letter-spacing:0.06em;text-transform:uppercase;color:#6e7681;margin-bottom:6px;">
                    <span>Low</span><span>High</span>
                </div>
                <div style="background:#21262d;border-radius:4px;height:6px;overflow:hidden;">
                    <div style="width:${fill}%;height:100%;background:${color};border-radius:4px;transition:width 0.5s ease;"></div>
                </div>
                <p style="text-align:center;margin-top:10px;font-size:13px;color:#8b949e;">
                    Estimated risk: <strong style="color:#e6edf3;font-family:'DM Mono',monospace;">${fill.toFixed(0)}%</strong>
                </p>
            </div>`;
    }

    const lbl = disease === 'diabetes'
        ? diabetesResultLabel(positive, data.severity)
        : { headline: `${disease.charAt(0).toUpperCase()+disease.slice(1)} — ${positive ? 'Positive' : 'Negative'}`,
            accent: positive ? '#f85149' : '#3fb950',
            bg:     positive ? 'rgba(248,81,73,0.08)'  : 'rgba(63,185,80,0.08)',
            border: positive ? 'rgba(248,81,73,0.25)'  : 'rgba(63,185,80,0.25)' };

    let html = `
        <div style="background:${lbl.bg};border:1px solid ${lbl.border};border-radius:12px;padding:32px 36px;margin-bottom:20px;text-align:center;">
            <h2 style="font-size:1.35rem;font-weight:600;letter-spacing:-0.02em;color:${lbl.accent};margin-bottom:4px;">${lbl.headline}</h2>
            ${disease === 'diabetes' ? riskMeter(pct) : `<p style="font-size:0.9rem;color:#8b949e;margin-top:8px;">Confidence score: <strong style="color:#e6edf3;font-family:'DM Mono',monospace;">${pct}%</strong></p>`}
            ${data.seek_medical_attention
                ? '<div style="margin-top:20px;padding:12px 18px;background:rgba(248,81,73,0.1);border:1px solid rgba(248,81,73,0.3);border-radius:6px;font-size:0.875rem;font-weight:500;color:#f85149;">Please see a doctor as soon as possible</div>'
                : ''}
            ${disease === 'diabetes' && window._lastBMI ? (() => {
                const b   = window._lastBMI;
                const cat = b < 18.5 ? 'Underweight' : b < 25 ? 'Healthy weight' : b < 30 ? 'Overweight' : 'Obese';
                const col = b < 25 ? '#3fb950' : b < 30 ? '#d29922' : '#f85149';
                return `<p style="margin-top:14px;font-size:0.8rem;color:#8b949e;">Your BMI: <strong style="color:${col};font-family:'DM Mono',monospace;">${b.toFixed(1)}</strong> — <span style="color:${col};">${cat}</span>${b >= 25 ? ' · Elevated weight is a known diabetes risk factor.' : ''}</p>`;
            })() : ''}
            <p style="margin-top:${disease==='diabetes'?'12':'16'}px;font-size:0.75rem;color:#6e7681;">This is a screening tool — not a medical diagnosis. Always confirm results with a healthcare provider.</p>
        </div>
        <div style="background:#161b22;border:1px solid #30363d;border-radius:12px;padding:28px 32px;">
            <p style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#6e7681;margin-bottom:16px;">What to do next</p>
            <ul style="list-style:none;padding:0;display:grid;gap:8px;">
                ${(data.recommendations || []).map(r => `<li style="padding:12px 16px;background:#1c2330;border-left:3px solid #4f8ef7;border-radius:0 6px 6px 0;font-size:0.875rem;color:#e6edf3;line-height:1.55;">${r}</li>`).join('')}
            </ul>
        </div>`;

    document.getElementById('resultContent').innerHTML = html;
    document.getElementById('diagnosisForm').style.display = 'none';
    document.getElementById('results').style.display       = 'block';
    loadMyDiagnosesCount();
}

// ── HISTORY ───────────────────────────────────────────────────────────────────
async function loadMyHistory() {
    const container = document.getElementById('historyContainer');
    container.innerHTML = '<p style="text-align:center;color:#999">Loading…</p>';

    const { ok, data } = await api('/diagnoses/my-history');
    if (!ok) { container.innerHTML = '<p style="color:red">Failed to load history.</p>'; return; }
    if (!data.length) { container.innerHTML = '<p style="text-align:center;color:#999">No diagnosis history yet.</p>'; return; }

    container.innerHTML = data.map(diag => `
        <div class="history-card">
            <div class="history-header">
                <h3>${diag.disease.charAt(0).toUpperCase() + diag.disease.slice(1)}</h3>
                <span class="badge ${diag.prediction === 1 ? 'positive' : 'negative'}">
                    ${diag.prediction === 1 ? 'Positive' : 'Negative'}
                </span>
            </div>
            <p><strong>Date:</strong> ${new Date(diag.created_at).toLocaleDateString()}</p>
            <p><strong>Confidence:</strong> ${(diag.probability * 100).toFixed(2)}%</p>
            <p><strong>Severity:</strong> ${diag.severity}</p>
        </div>`).join('');
}

async function loadMyDiagnosesCount() {
    const { ok, data } = await api('/diagnoses/my-history');
    if (ok) document.getElementById('myDiagnosesCount').textContent = data.length;
}

// ── PROFILE ───────────────────────────────────────────────────────────────────
function loadProfile() {
    if (!currentUser) return;
    document.getElementById('profileFullName').value = currentUser.full_name || '';
    document.getElementById('profileEmail')   .value = currentUser.email     || '';
    document.getElementById('profileAge')     .value = currentUser.age       || '';
    document.getElementById('profileGender')  .value = currentUser.gender    || '';
    document.getElementById('profilePhone')   .value = currentUser.phone     || '';
}

async function handleProfileUpdate() {
    const errDiv = document.getElementById('profileError');
    const okDiv  = document.getElementById('profileSuccess');
    errDiv.style.display = 'none'; okDiv.style.display = 'none';

    const { ok, data } = await api('/profile', {
        method: 'PUT',
        body  : JSON.stringify({
            full_name: document.getElementById('profileFullName').value,
            email    : document.getElementById('profileEmail').value,
            age      : document.getElementById('profileAge').value    || null,
            gender   : document.getElementById('profileGender').value || null,
            phone    : document.getElementById('profilePhone').value  || null,
        })
    });

    if (ok) {
        currentUser = data.user; saveUser(currentUser);
        document.getElementById('userInfo').innerHTML = `<i class="fas fa-user-circle"></i> ${currentUser.full_name}`;
        okDiv.textContent = 'Profile updated!'; okDiv.style.display = 'block';
    } else {
        errDiv.textContent = data.error || 'Update failed'; errDiv.style.display = 'block';
    }
}

async function handlePasswordChange() {
    const errDiv = document.getElementById('profileError');
    const okDiv  = document.getElementById('profileSuccess');
    errDiv.style.display = 'none'; okDiv.style.display = 'none';

    const { ok, data } = await api('/profile/password', {
        method: 'PUT',
        body  : JSON.stringify({
            old_password: document.getElementById('oldPassword').value,
            new_password: document.getElementById('newPassword').value,
        })
    });

    if (ok) {
        okDiv.textContent = 'Password changed!'; okDiv.style.display = 'block';
        document.getElementById('passwordForm').reset();
    } else {
        errDiv.textContent = data.error || 'Failed'; errDiv.style.display = 'block';
    }
}

// ── ADMIN ─────────────────────────────────────────────────────────────────────
async function loadAdminDashboard() {
    await loadAdminStats();
    await loadAllUsers();
}

async function loadAdminStats() {
    const { ok, data } = await api('/admin/statistics');
    if (!ok) return;
    document.getElementById('adminStats').innerHTML = `
        <div class="admin-stat-card"><h3>${data.total_users}</h3><p>Total Users</p></div>
        <div class="admin-stat-card"><h3>${data.active_users}</h3><p>Active Users</p></div>
        <div class="admin-stat-card"><h3>${data.inactive_users}</h3><p>Inactive Users</p></div>
        <div class="admin-stat-card"><h3>${data.total_diagnoses}</h3><p>Total Diagnoses</p></div>
        <div class="admin-stat-card"><h3>${data.diabetes_positive}</h3><p>Diabetes Cases</p></div>
        <div class="admin-stat-card"><h3>${data.malaria_positive}</h3><p>Malaria Cases</p></div>`;
}

async function loadAllUsers() {
    const { ok, data } = await api('/admin/users');
    if (!ok) return;

    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = data
        .filter(u => u.username !== 'admin')
        .map(u => `
            <tr>
                <td>${u.username}${u.is_admin ? ' <span class="status-badge status-admin">Admin</span>' : ''}</td>
                <td>${u.full_name}</td>
                <td>${u.email}</td>
                <td><span class="status-badge ${u.is_active ? 'status-active' : 'status-inactive'}">${u.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>${u.diagnosis_count ?? '-'}</td>
                <td>${new Date(u.created_at).toLocaleDateString()}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon btn-view"   onclick="viewUserDetails(${u.id})" title="View"><i class="fas fa-eye"></i></button>
                        <button class="btn-icon btn-edit"   onclick="editUser(${u.id})"        title="Edit"><i class="fas fa-edit"></i></button>
                        <button class="btn-icon btn-delete" onclick="deleteUser(${u.id},'${u.username}')" title="Delete"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            </tr>`).join('');
}

async function viewUserDetails(userId) {
    const { ok, data } = await api(`/admin/users/${userId}/diagnoses`);
    if (!ok) { alert('Failed to load user details'); return; }

    const { user, diagnoses } = data;
    document.getElementById('userModalContent').innerHTML = `
        <div class="user-details-grid">
            <div class="user-detail"><label>Username</label><strong>${user.username}</strong></div>
            <div class="user-detail"><label>Full Name</label><strong>${user.full_name}</strong></div>
            <div class="user-detail"><label>Email</label><strong>${user.email}</strong></div>
            <div class="user-detail"><label>Phone</label><strong>${user.phone || 'N/A'}</strong></div>
            <div class="user-detail"><label>Age</label><strong>${user.age || 'N/A'}</strong></div>
            <div class="user-detail"><label>Gender</label><strong>${user.gender || 'N/A'}</strong></div>
            <div class="user-detail"><label>Status</label><strong>${user.is_active ? 'Active' : 'Inactive'}</strong></div>
            <div class="user-detail"><label>Joined</label><strong>${new Date(user.created_at).toLocaleDateString()}</strong></div>
        </div>
        <h3 style="margin-top:20px">Diagnosis History (${diagnoses.length})</h3>
        ${!diagnoses.length ? '<p style="color:#999">No diagnoses yet.</p>' :
            diagnoses.map(d => `
                <div class="history-card" style="margin-top:10px">
                    <div class="history-header">
                        <h4>${d.disease.charAt(0).toUpperCase() + d.disease.slice(1)}</h4>
                        <span class="badge ${d.prediction === 1 ? 'positive' : 'negative'}">${d.prediction === 1 ? 'Positive' : 'Negative'}</span>
                    </div>
                    <p><strong>Date:</strong> ${new Date(d.created_at).toLocaleString()}</p>
                    <p><strong>Confidence:</strong> ${(d.probability * 100).toFixed(2)}%</p>
                    <p><strong>Severity:</strong> ${d.severity}</p>
                </div>`).join('')}`;

    document.getElementById('userModal').style.display = 'flex';
}

function closeUserModal() { document.getElementById('userModal').style.display = 'none'; }

async function editUser(userId) {
    const { ok, data } = await api(`/admin/users/${userId}`);
    if (!ok) { alert('Failed to load user'); return; }
    document.getElementById('editUserId')  .value   = data.id;
    document.getElementById('editUsername').value   = data.username;
    document.getElementById('editFullName').value   = data.full_name;
    document.getElementById('editEmail')   .value   = data.email;
    document.getElementById('editAge')     .value   = data.age    || '';
    document.getElementById('editGender')  .value   = data.gender || '';
    document.getElementById('editPhone')   .value   = data.phone  || '';
    document.getElementById('editIsActive').checked = data.is_active;
    document.getElementById('editUserModal').style.display = 'flex';
}

function closeEditUserModal() { document.getElementById('editUserModal').style.display = 'none'; }

async function handleUpdateUser() {
    const userId = document.getElementById('editUserId').value;
    const { ok, data } = await api(`/admin/users/${userId}`, {
        method: 'PUT',
        body  : JSON.stringify({
            username : document.getElementById('editUsername').value,
            full_name: document.getElementById('editFullName').value,
            email    : document.getElementById('editEmail').value,
            age      : document.getElementById('editAge').value    || null,
            gender   : document.getElementById('editGender').value || null,
            phone    : document.getElementById('editPhone').value  || null,
            is_active: document.getElementById('editIsActive').checked,
        })
    });
    if (ok) { alert('User updated!'); closeEditUserModal(); loadAllUsers(); }
    else    { alert(data.error || 'Update failed'); }
}

async function deleteUser(userId, username) {
    if (!confirm(`Delete user "${username}"? This cannot be undone.`)) return;
    const { ok, data } = await api(`/admin/users/${userId}`, { method: 'DELETE' });
    if (ok) { alert('User deleted!'); loadAllUsers(); loadAdminStats(); }
    else    { alert(data.error || 'Delete failed'); }
}

function showCreateUserModal() {
    document.getElementById('createUserForm').reset();
    document.getElementById('createUserError').style.display = 'none';
    document.getElementById('createUserModal').style.display = 'flex';
}

function closeCreateUserModal() { document.getElementById('createUserModal').style.display = 'none'; }

async function handleCreateUser() {
    const errDiv = document.getElementById('createUserError');
    errDiv.style.display = 'none';

    const { ok, data } = await api('/admin/users', {
        method: 'POST',
        body  : JSON.stringify({
            username : document.getElementById('createUsername').value,
            password : document.getElementById('createPassword').value,
            full_name: document.getElementById('createFullName').value,
            email    : document.getElementById('createEmail').value,
            age      : document.getElementById('createAge').value    || null,
            gender   : document.getElementById('createGender').value || null,
            phone    : document.getElementById('createPhone').value  || null,
            is_admin : document.getElementById('createIsAdmin').checked,
        })
    });

    if (ok) {
        alert('User created successfully!');
        closeCreateUserModal();
        loadAllUsers();
        loadAdminStats();
    } else {
        errDiv.textContent  = data.error || 'Failed to create user';
        errDiv.style.display = 'block';
    }
}

// ── MODAL CLOSE ON OUTSIDE CLICK ──────────────────────────────────────────────
window.onclick = function(e) {
    if (e.target === document.getElementById('userModal'))       closeUserModal();
    if (e.target === document.getElementById('editUserModal'))   closeEditUserModal();
    if (e.target === document.getElementById('createUserModal')) closeCreateUserModal();
};
