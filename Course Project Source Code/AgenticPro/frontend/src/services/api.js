const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
const API_URL = `${API_BASE}/api`;

async function request(path, options = {}) {
  const url = path.startsWith('http')
    ? path
    : path.startsWith('/api')
    ? `${API_BASE}${path}`
    : `${API_URL}${path}`;

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        detail = errorData.detail || errorData.message || detail;
      } catch {
        // fallback to status text
        detail = response.statusText || detail;
      }
      throw new Error(detail);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${path}]:`, error);
    throw error;
  }
}

export const api = {
  // Auth
  login: (credentials) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),
  register: (userData) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),
  updateProfile: (profileData) =>
    request('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    }),
  getUsers: (role) =>
    request(`/auth/users${role ? `?role=${role}` : ''}`),

  // Health & stats
  getHealth: () => request(`${API_BASE}/health`),
  getStats: () => request('/stats'),

  // Exams
  getExams: () => request('/exams'),
  getExam: (id) => request(`/exams/${id}`),
  createExam: (examData) =>
    request('/exams', {
      method: 'POST',
      body: JSON.stringify(examData),
    }),
  deleteExam: (id) =>
    request(`/exams/${id}`, {
      method: 'DELETE',
    }),
  addQuestionToExam: (examId, questionId) =>
    request(`/exams/${examId}/questions/${questionId}`, {
      method: 'POST',
    }),

  // Questions
  getQuestions: () => request('/questions'),
  getQuestion: (id) => request(`/questions/${id}`),
  createQuestion: (questionData) =>
    request('/questions', {
      method: 'POST',
      body: JSON.stringify(questionData),
    }),
  generateQuestion: (params) =>
    request('/questions/generate', {
      method: 'POST',
      body: JSON.stringify(params),
    }),
  deleteQuestion: (id) =>
    request(`/questions/${id}`, {
      method: 'DELETE',
    }),

  // Test Cases
  getTestCases: (questionId, includeHidden = false) =>
    request(`/test-cases/question/${questionId}?include_hidden=${includeHidden}`),
  createTestCase: (testCaseData) =>
    request('/test-cases', {
      method: 'POST',
      body: JSON.stringify(testCaseData),
    }),

  // Submissions & Execution
  getSubmissions: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/submissions${query ? `?${query}` : ''}`);
  },
  getSubmission: (id) => request(`/submissions/${id}`),
  submit: (submission) =>
    request('/submissions', {
      method: 'POST',
      body: JSON.stringify(submission),
    }),
  runCodeDirectly: (codeData) =>
    request('/evaluations/run-code', {
      method: 'POST',
      body: JSON.stringify(codeData),
    }),
  runEvaluation: (submissionId) =>
    request(`/evaluations/${submissionId}/run`, {
      method: 'POST',
    }),
  getEvaluation: (submissionId) => request(`/evaluations/${submissionId}`),

  // Results
  getResults: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/results${query ? `?${query}` : ''}`);
  },
  getResult: (examId, studentId) => request(`/results/${examId}/${studentId}`),
  publishResult: (examId, studentId, published = true) =>
    request(`/results/publish/${examId}/${studentId}`, {
      method: 'POST',
      body: JSON.stringify({ published }),
    }),

  // Lab 9: Deep Research Agent
  runResearch: (researchRequest) =>
    request('/research/briefing', {
      method: 'POST',
      body: JSON.stringify(researchRequest),
    }),
  getResearchReports: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/research/reports${query ? `?${query}` : ''}`);
  },
  getResearchReport: (reportId) => request(`/research/reports/${reportId}`),
  deleteResearchReport: (reportId) =>
    request(`/research/reports/${reportId}`, {
      method: 'DELETE',
    }),
  exportEvidence: (exportRequest) =>
    request('/research/export-evidence', {
      method: 'POST',
      body: JSON.stringify(exportRequest),
    }),

  // Lab 10: Cloud Operations Agent
  diagnoseDeployment: (diagnosisRequest) =>
    request('/cloud-ops/diagnose', {
      method: 'POST',
      body: JSON.stringify(diagnosisRequest),
    }),
  getIncidents: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/cloud-ops/incidents${query ? `?${query}` : ''}`);
  },
  getIncident: (incidentId) => request(`/cloud-ops/incidents/${incidentId}`),
  applyIncidentRemediation: (incidentId, data = {}) =>
    request(`/cloud-ops/incidents/${incidentId}/apply`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteIncident: (incidentId) =>
    request(`/cloud-ops/incidents/${incidentId}`, {
      method: 'DELETE',
    }),
  exportPostmortem: (exportRequest) =>
    request('/cloud-ops/export-postmortem', {
      method: 'POST',
      body: JSON.stringify(exportRequest),
    }),

  // Lab 11: Agentic SDLC Factory
  runSDLCPipeline: (requestData) =>
    request('/sdlc/pipeline', {
      method: 'POST',
      body: JSON.stringify(requestData),
    }),
  getSDLCProjects: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/sdlc/projects${query ? `?${query}` : ''}`);
  },
  getSDLCProject: (projectId) => request(`/sdlc/projects/${projectId}`),
  runSDLCTests: (projectId) =>
    request(`/sdlc/projects/${projectId}/run-tests`, {
      method: 'POST',
    }),
  deleteSDLCProject: (projectId) =>
    request(`/sdlc/projects/${projectId}`, {
      method: 'DELETE',
    }),
  getSDLCZipUrl: (projectId) => `${API_URL}/sdlc/projects/${projectId}/export`,

  // Lab 12: Safety & Governance Agent
  assessActionSafety: (assessmentRequest) =>
    request('/governance/assess', {
      method: 'POST',
      body: JSON.stringify(assessmentRequest),
    }),
  getSafetyAudits: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/governance/audits${query ? `?${query}` : ''}`);
  },
  getSafetyAudit: (auditId) => request(`/governance/audits/${auditId}`),
  recordApprovalDecision: (auditId, decisionData) =>
    request(`/governance/audits/${auditId}/decision`, {
      method: 'POST',
      body: JSON.stringify(decisionData),
    }),
  executeAuditRollback: (auditId, rollbackData) =>
    request(`/governance/audits/${auditId}/rollback`, {
      method: 'POST',
      body: JSON.stringify(rollbackData),
    }),
  deleteSafetyAudit: (auditId) =>
    request(`/governance/audits/${auditId}`, {
      method: 'DELETE',
    }),
  exportGovernanceReport: (exportRequest) =>
    request('/governance/export-report', {
      method: 'POST',
      body: JSON.stringify(exportRequest),
    }),

  // Lab 13: Discipline-Specific Agents (ME / CE / EE)
  solveDisciplineWorklet: (solveRequest) =>
    request('/discipline/solve', {
      method: 'POST',
      body: JSON.stringify(solveRequest),
    }),
  getDisciplineWorklets: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/discipline/worklets${query ? `?${query}` : ''}`);
  },
  getDisciplineWorklet: (workletId) => request(`/discipline/worklets/${workletId}`),
  runDisciplineCode: (workletId, data = {}) =>
    request(`/discipline/worklets/${workletId}/run-code`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteDisciplineWorklet: (workletId) =>
    request(`/discipline/worklets/${workletId}`, {
      method: 'DELETE',
    }),
  exportDisciplineReport: (exportRequest) =>
    request('/discipline/export', {
      method: 'POST',
      body: JSON.stringify(exportRequest),
    }),

  // Lab 14: Capstone Project Studio
  createCapstoneProject: (projectData) =>
    request('/capstone/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    }),
  getCapstoneProjects: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/capstone/projects${query ? `?${query}` : ''}`);
  },
  getCapstoneProject: (projectId) => request(`/capstone/projects/${projectId}`),
  runCapstoneStage: (projectId, stageData = {}) =>
    request(`/capstone/projects/${projectId}/run-stage`, {
      method: 'POST',
      body: JSON.stringify(stageData),
    }),
  runCapstoneTests: (projectId, testData = {}) =>
    request(`/capstone/projects/${projectId}/run-tests`, {
      method: 'POST',
      body: JSON.stringify(testData),
    }),
  deleteCapstoneProject: (projectId) =>
    request(`/capstone/projects/${projectId}`, {
      method: 'DELETE',
    }),
  getCapstoneZipUrl: (projectId) => `${API_URL}/capstone/projects/${projectId}/export-zip`,
  exportCapstoneReport: (exportRequest) =>
    request('/capstone/export-report', {
      method: 'POST',
      body: JSON.stringify(exportRequest),
    }),
};
