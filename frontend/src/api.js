
import axios from 'axios';

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    'http://127.0.0.1:8000/api',
  timeout: 120000, // Long source-analysis and report requests may need more than 30 seconds.
});

// Attach JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('bug_detective_token');

    if (token) {
      config.headers = config.headers || {};
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Handle API errors and expired sessions
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('bug_detective_token');
      localStorage.removeItem('bug_detective_user');

      if (window.location.pathname !== '/login') {
        window.location.assign('/login');
      }
    }

    return Promise.reject(error);
  }
);

// Display readable error messages
export const messageOf = (error) => {
  if (error?.code === 'ERR_NETWORK' || (!error?.response && error?.request)) {
    return 'Cannot reach the backend API at http://127.0.0.1:8000. Start the FastAPI server in its terminal and check /api/health.';
  }
  if (error?.code === 'ECONNABORTED') {
    return 'The request took longer than 120 seconds. For large projects, use Queue background scan and keep the worker running.';
  }
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg || 'Invalid input')
      .join(', ');
  }

  if (typeof detail === 'string') {
    return detail;
  }

  return (
    error?.message ||
    'Unexpected error. Please try again.'
  );
};

export default api;

export const getLocalTestReport = async () => {
  const response = await api.get('/test-runner/local-report');
  return response.data;
};

export const downloadProjectTestReportExcel = async (uploadId) => {
  const response = await api.get(
    `/projects/${encodeURIComponent(uploadId)}/test-report/excel`,
    {
      responseType: 'blob',
    }
  );

  return response.data;
};

export const downloadTestCasesExcel = async () => {
  const response = await api.get('/test-cases/excel', {
    responseType: 'blob',
  });

  return response.data;
};

export const executeProjectTests = async (uploadId) => {
  const response = await api.post(
    `/projects/${encodeURIComponent(uploadId)}/execute-tests`
  );

  return response.data;
};
