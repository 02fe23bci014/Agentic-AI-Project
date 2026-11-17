import { useState } from 'react';
import { api } from '../services/api';

export default function EditProfileModal({ currentUser, onClose, onUpdateSuccess }) {
  const [fullName, setFullName] = useState(currentUser.full_name || currentUser.username || '');
  const [email, setEmail] = useState(currentUser.email || '');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = {
        user_id: currentUser.id,
        full_name: fullName.trim() || currentUser.username,
        email: email.trim() || null,
      };

      if (newPassword.trim()) {
        payload.password = newPassword.trim();
      }

      const updatedUser = await api.updateProfile(payload);
      onUpdateSuccess(updatedUser);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card profile-edit-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="eyebrow">Account Settings</div>
            <h3>Edit Profile Details</h3>
          </div>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {error && (
          <div className="login-error-alert" role="alert">
            <span className="error-icon">⚠</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="admin-form">
          {/* Read-Only Account Metadata */}
          <div className="profile-meta-card">
            <div className="meta-row">
              <span className="meta-label">Username:</span>
              <strong className="meta-value">@{currentUser.username}</strong>
            </div>
            <div className="meta-row">
              <span className="meta-label">Account Role:</span>
              <span className={`role-tag-pill ${currentUser.role === 'faculty' ? 'tag-faculty' : 'tag-student'}`}>
                {currentUser.role.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Editable Display / Profile Name */}
          <label className="form-label">
            <span>Profile / Display Name *</span>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Your name or nickname"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
            <small className="field-hint">
              This name is shown in the workspace and on published grade reports.
            </small>
          </label>

          {/* Email Address */}
          <label className="form-label">
            <span>Email Address</span>
            <input
              type="email"
              className="form-input"
              placeholder="e.g. user@university.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          {/* Optional Password Update */}
          <label className="form-label">
            <span>New Password (Leave blank to keep current)</span>
            <input
              type="password"
              className="form-input"
              placeholder="Enter new password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
            />
          </label>

          <div className="modal-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading ? 'Saving Changes…' : 'Save Profile Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
