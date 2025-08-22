import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Container
} from '@mui/material';
import { AccountBalance, Login as LoginIcon } from '@mui/icons-material';
import { apiService } from '../../services/api';
import { setCurrentUserId } from '../../config/constants';

interface LoginProps {
  onLoginSuccess: (user: any) => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const demoUsers = [
    {
      email: 'conservative@finvoice.com',
      password: 'password123',
      type: 'Conservative Investor',
      description: 'Safe investments, stable returns'
    },
    {
      email: 'aggressive@finvoice.com',
      password: 'password123',
      type: 'Aggressive Investor',
      description: 'High-risk, high-reward portfolio'
    }
  ];

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await apiService.loginUser(email, password);
      
      if (response.success) {
        localStorage.setItem('currentUser', JSON.stringify(response.user));
        setCurrentUserId(response.user.id);
        onLoginSuccess(response.user);
        // Navigate will be handled by App.tsx routing
      } else {
        setError('Login failed. Please try again.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (demoUser: any) => {
    setEmail(demoUser.email);
    setPassword(demoUser.password);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <AccountBalance sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
            FinVoice
          </Typography>
          <Typography variant="h6" color="textSecondary">
            AI-Powered Financial Management Platform
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 4 }}>
          {/* Login Form */}
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LoginIcon />
                Login to Your Account
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <Box component="form" onSubmit={handleLogin} sx={{ mt: 2 }}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  margin="normal"
                  required
                  variant="outlined"
                />
                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  margin="normal"
                  required
                  variant="outlined"
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ mt: 3, mb: 2 }}
                >
                  {loading ? <CircularProgress size={24} /> : 'Login'}
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Demo Users */}
          <Card sx={{ flex: 1 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Demo Accounts
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                Try our platform with pre-configured demo accounts
              </Typography>

              {demoUsers.map((user, index) => (
                <Card 
                  key={index} 
                  variant="outlined" 
                  sx={{ 
                    mb: 2, 
                    cursor: 'pointer',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                  onClick={() => handleDemoLogin(user)}
                >
                  <CardContent sx={{ py: 2 }}>
                    <Typography variant="h6" color="primary">
                      {user.type}
                    </Typography>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      {user.description}
                    </Typography>
                    <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                      {user.email}
                    </Typography>
                  </CardContent>
                </Card>
              ))}

              <Alert severity="info" sx={{ mt: 2 }}>
                Click on any demo account to auto-fill login credentials, then click Login.
              </Alert>
            </CardContent>
          </Card>
        </Box>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            Experience real-time portfolio tracking, AI-powered insights, and comprehensive financial management
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Login;
