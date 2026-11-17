import { useState, useEffect } from 'react';
import EditProfileModal from './components/EditProfileModal.jsx';
import ExamPage from './pages/ExamPage.jsx';
import FacultyDashboard from './pages/FacultyDashboard.jsx';
import LoginPage from './pages/LoginPage.jsx';
import ResultsPage from './pages/ResultsPage.jsx';
import StudentDashboard from './pages/StudentDashboard.jsx';
import DeepResearchPage from './pages/DeepResearchPage.jsx';
import CloudOpsPage from './pages/CloudOpsPage.jsx';
import SDLCFactoryPage from './pages/SDLCFactoryPage.jsx';
import SafetyGovernancePage from './pages/SafetyGovernancePage.jsx';
import DisciplineAgentsPage from './pages/DisciplineAgentsPage.jsx';
import CapstoneStudioPage from './pages/CapstoneStudioPage.jsx';
import SwarmMonitor from './components/SwarmMonitor.jsx';
import { api } from './services/api';
import './styles.css';

const STUDENT_VIEWS = [
  { id: 'Labs', label: 'My Labs' },
  { id: 'Results', label: 'My Results & Grades' },
];

const FACULTY_VIEWS = [
  { id: 'Faculty', label: 'Faculty Dashboard' },
  { id: 'Results', label: 'Gradebook & Publishing' },
  { id: 'Swarm', label: 'Swarm Architecture' },
];

export default function App() {
  // Authentication session
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const stored = localStorage.getItem('agenticpro_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const [authToken, setAuthToken] = useState(() => {
    return localStorage.getItem('agenticpro_token') || null;
  });

  // Profile Edit Modal & Notification
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  // Navigation
  const [view, setView] = useState('Labs');
  const [inExam, setInExam] = useState(false);
  const [activeExam, setActiveExam] = useState(null);
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    checkApiHealth();
    const interval = setInterval(checkApiHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // When user role changes or logs in, set default view
  useEffect(() => {
    if (currentUser) {
      if (currentUser.role === 'faculty') {
        setView('Faculty');
      } else {
        setView('Labs');
      }
    }
  }, [currentUser?.role]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3500);
  };

  const checkApiHealth = async () => {
    try {
      await api.getHealth();
      setApiOnline(true);
    } catch {
      setApiOnline(false);
    }
  };

  const handleLoginSuccess = (user, token) => {
    setCurrentUser(user);
    setAuthToken(token);
    localStorage.setItem('agenticpro_user', JSON.stringify(user));
    localStorage.setItem('agenticpro_token', token);
    setInExam(false);
    setActiveExam(null);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setAuthToken(null);
    localStorage.removeItem('agenticpro_user');
    localStorage.removeItem('agenticpro_token');
    setInExam(false);
    setActiveExam(null);
  };

  const handleProfileUpdated = (updatedUser) => {
    setCurrentUser(updatedUser);
    localStorage.setItem('agenticpro_user', JSON.stringify(updatedUser));
    showToast('Profile updated successfully!');
  };

  const startExam = (exam) => {
    setActiveExam(exam);
    setInExam(true);
  };

  const exitExam = () => {
    setInExam(false);
    setActiveExam(null);
    setView('Labs');
  };

  // If not authenticated, render Login Page
  if (!currentUser) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  const isFaculty = currentUser.role === 'faculty';
  const currentNavItems = isFaculty ? FACULTY_VIEWS : STUDENT_VIEWS;

  return (
    <div className="app-shell">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="toast-notification toast-success">{toastMessage}</div>
      )}

      {/* Top Application Header */}
      <header className="topbar">
        <div className="topbar-left">
          <a
            className="brand"
            href="#home"
            onClick={(e) => {
              e.preventDefault();
              if (inExam) exitExam();
            }}
          >
            <span className="brand-mark">AP</span>
            <div className="brand-titles">
              <span className="brand-name">AgenticPro</span>
              <small className="brand-tagline">
                {isFaculty ? 'Faculty Management Portal' : 'Student Laboratory Portal'}
              </small>
            </div>
          </a>
        </div>

        {!inExam && (
          <nav aria-label="Main navigation" className="main-nav">
            {currentNavItems.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`nav-link ${view === item.id ? 'active' : ''}`}
                onClick={() => setView(item.id)}
              >
                {item.label}
              </button>
            ))}
          </nav>
        )}

        <div className="header-user-section">
          {/* API Health Pill */}
          <div
            className={`api-status-pill ${apiOnline ? 'api-online' : 'api-offline'}`}
            title={apiOnline ? 'Connected to FastAPI backend' : 'Backend offline or reconnecting'}
          >
            <span className="api-dot" />
            <span className="api-label">{apiOnline ? 'Connected' : 'Offline'}</span>
          </div>

          {/* User Profile Pill - Displays Username Prominently */}
          <div className="user-profile-badge">
            <span className={`role-avatar-icon ${isFaculty ? 'avatar-faculty' : 'avatar-student'}`}>
              {isFaculty ? '👨‍🏫' : '👨‍🎓'}
            </span>
            <div className="user-badge-info">
              {/* Only the username is displayed here */}
              <strong className="badge-name">{currentUser.username}</strong>
              <div className="badge-meta">
                <span className={`role-tag-pill ${isFaculty ? 'tag-faculty' : 'tag-student'}`}>
                  {currentUser.role.toUpperCase()}
                </span>
                {currentUser.full_name && currentUser.full_name !== currentUser.username && (
                  <span className="badge-fullname" title="Display Name">
                    ({currentUser.full_name})
                  </span>
                )}
              </div>
            </div>

            {/* Edit Profile Button */}
            <button
              type="button"
              className="badge-edit-btn"
              onClick={() => setShowProfileModal(true)}
              title="Edit Profile Name & Details"
            >
              ✏️ Edit
            </button>
          </div>

          {/* Logout Button */}
          <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
            title="Sign out of AgenticPro"
          >
            <span>Sign Out</span>
            <span aria-hidden="true">↳</span>
          </button>
        </div>
      </header>

      {/* Main View Router */}
      <main className="main-content-wrapper">
        {/* Student View Options */}
        {!isFaculty && (
          <>
            {inExam ? (
              <ExamPage
                exam={activeExam}
                onExit={exitExam}
                currentStudentId={currentUser.username}
              />
            ) : view === 'Labs' ? (
              <StudentDashboard
                onStart={startExam}
                currentStudentId={currentUser.username}
              />
            ) : (
              <ResultsPage
                isFaculty={false}
                currentStudentId={currentUser.username}
              />
            )}
          </>
        )}

        {/* Faculty View Options */}
        {isFaculty && (
          <>
            {view === 'Faculty' ? (
              <FacultyDashboard />
            ) : view === 'Results' ? (
              <ResultsPage
                isFaculty={true}
                currentStudentId={currentUser.username}
              />
            ) : (
              <SwarmMonitor />
            )}
          </>
        )}
      </main>

      {/* Edit Profile Modal */}
      {showProfileModal && (
        <EditProfileModal
          currentUser={currentUser}
          onClose={() => setShowProfileModal(false)}
          onUpdateSuccess={handleProfileUpdated}
        />
      )}

      {/* Modern Footer */}
      <footer className="app-footer">
        <div className="footer-left">
          <strong>AgenticPro Assessment Suite</strong>
          <span>
            Signed in as @{currentUser.username} ({currentUser.role.toUpperCase()}) · Role-Guarded Workspace
          </span>
        </div>
        <div className="footer-right">
          <span>FastAPI Backend · React 19 UI · SQLite Persistence</span>
        </div>
      </footer>
    </div>
  );
}
