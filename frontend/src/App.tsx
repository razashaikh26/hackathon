import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from 'react-query';

// Components
import Layout from './components/Layout/Layout';
import Login from './components/Auth/Login';
import ChatBot from './components/ChatBot/ChatBot';
import Dashboard from './pages/Dashboard/Dashboard';
import Portfolio from './pages/Portfolio/Portfolio';
import Expenses from './pages/Expenses/Expenses';
import Goals from './pages/Goals/GoalsNew';
import Insights from './pages/Insights/Insights';
import VoiceInput from './pages/VoiceInput/VoiceInput';
import Settings from './pages/Settings/Settings';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

function AppContent() {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('currentUser');
      }
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (user: any) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    localStorage.removeItem('currentUser');
    setCurrentUser(null);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        Loading...
      </div>
    );
  }

  return (
    <Routes>
      {/* Login Route */}
      <Route 
        path="/login" 
        element={
          currentUser ? <Navigate to="/dashboard" replace /> : <Login onLoginSuccess={handleLoginSuccess} />
        } 
      />
      
      {/* Protected Routes */}
      {currentUser ? (
        <>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route 
            path="/*" 
            element={
              <Layout onLogout={handleLogout}>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/portfolio" element={<Portfolio />} />
                  <Route path="/expenses" element={<Expenses />} />
                  <Route path="/goals" element={<Goals />} />
                  <Route path="/insights" element={<Insights />} />
                  <Route path="/voice" element={<VoiceInput />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
                <ChatBot />
              </Layout>
            } 
          />
        </>
      ) : (
        <>
          {/* Redirect all routes to login when not authenticated */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/*" element={<Navigate to="/login" replace />} />
        </>
      )}
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <AppContent />
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
