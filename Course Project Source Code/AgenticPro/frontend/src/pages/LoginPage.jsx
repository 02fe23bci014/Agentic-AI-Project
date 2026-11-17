import { useState } from 'react';
import { api } from '../services/api';

export default function LoginPage({ onLoginSuccess }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [selectedRole, setSelectedRole] = useState('student'); // 'student' | 'faculty'

  // Form Fields
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // States
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleRoleChange = (role) => {
    setSelectedRole(role);
    setErrorMessage('');
  };

  const handleQuickFill = (u, p, role) => {
    setSelectedRole(role);
    setUsername(u);
    setPassword(p);
    setErrorMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setLoading(true);

    try {
      if (mode === 'login') {
        const response = await api.login({
          username: username.trim(),
          password: password,
          role: selectedRole,
        });
        onLoginSuccess(response.user, response.token);
      } else {
        const response = await api.register({
          username: username.trim(),
          password: password,
          role: selectedRole,
          full_name: fullName.trim() || username.trim(),
          email: email.trim() || null,
        });
        onLoginSuccess(response.user, response.token);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page-container">
      <div className="login-card-shell">
        {/* Brand Header */}
        <div className="login-brand-header">
          <div className="brand-mark-lg">AP</div>
          <h2>AgenticPro Assessment Suite</h2>
          <p className="login-subtitle">
            Autonomous Multi-Agent Evaluation & Academic Code Lab
          </p>
        </div>

        {/* Step 1: Mandatory Role Selection */}
        <div className="role-selector-section">
          <label className="section-label">SELECT YOUR PORTAL</label>
          <div className="role-cards-grid">
            <button
              type="button"
              className={`role-select-card ${selectedRole === 'student' ? 'selected' : ''}`}
              onClick={() => handleRoleChange('student')}
            >
              <span className="role-icon">🎓</span>
              <div className="role-text-meta">
                <strong>Student Portal</strong>
                <small>Take exams & view evaluations</small>
              </div>
            </button>

            <button
              type="button"
              className={`role-select-card ${selectedRole === 'faculty' ? 'selected' : ''}`}
              onClick={() => handleRoleChange('faculty')}
            >
              <span className="role-icon">🏛️</span>
              <div className="role-text-meta">
                <strong>Faculty Portal</strong>
                <small>Curate labs & grade gradebooks</small>
              </div>
            </button>
          </div>
        </div>

        {/* Portal Info Banner */}
        <div className={`portal-info-banner banner-${selectedRole}`}>
          <span className="portal-indicator-dot" />
          <span>
            Signing in to <strong>{selectedRole === 'student' ? 'Student Workspace' : 'Faculty Management'}</strong>
          </span>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="login-error-alert" role="alert">
            <span className="error-icon">⚠</span>
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Login / Register Form */}
        <form onSubmit={handleSubmit} className="login-form">
          {mode === 'register' && (
            <>
              <label className="form-label">
                <span>Profile / Display Name (Optional)</span>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Leave empty to use username"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
              </label>

              <label className="form-label">
                <span>Email Address</span>
                <input
                  type="email"
                  className="form-input"
                  placeholder="e.g. alex@university.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </label>
            </>
          )}

          <label className="form-label">
            <span>Username *</span>
            <input
              type="text"
              className="form-input"
              placeholder={selectedRole === 'student' ? 'e.g. student1' : 'e.g. faculty1'}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </label>

          <label className="form-label">
            <span>Password *</span>
            <div className="password-input-wrap">
              <input
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                required
              />
              <button
                type="button"
                className="toggle-pw-btn"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '👁' : '👁‍🗨'}
              </button>
            </div>
          </label>

          <button
            type="submit"
            className="primary-button login-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <span className="btn-spinner-wrap">
                <span className="spinner-sm" /> Authenticating…
              </span>
            ) : mode === 'login' ? (
              `Sign In as ${selectedRole.toUpperCase()}`
            ) : (
              `Create ${selectedRole.toUpperCase()} Account`
            )}
          </button>
        </form>

        {/* Quick Demo Credentials */}
        <div className="quick-fill-section">
          <span className="quick-fill-label">ONE-CLICK DEMO CREDENTIALS</span>
          <div className="quick-fill-pills">
            <button
              type="button"
              className="quick-fill-pill"
              onClick={() => handleQuickFill('student1', 'student123', 'student')}
            >
              🎓 Student Demo (student1)
            </button>
            <button
              type="button"
              className="quick-fill-pill"
              onClick={() => handleQuickFill('faculty1', 'faculty123', 'faculty')}
            >
              🏛️ Faculty Demo (faculty1)
            </button>
          </div>
        </div>

        {/* Toggle Login / Register */}
        <div className="login-mode-switch">
          {mode === 'login' ? (
            <p>
              Don't have an account yet?{' '}
              <button
                type="button"
                className="link-btn"
                onClick={() => {
                  setMode('register');
                  setErrorMessage('');
                }}
              >
                Register Here
              </button>
            </p>
          ) : (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                className="link-btn"
                onClick={() => {
                  setMode('login');
                  setErrorMessage('');
                }}
              >
                Back to Sign In
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
