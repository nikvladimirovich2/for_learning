import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Container,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Cloud as CloudIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({
    authUrl: '',
    username: '',
    password: '',
    projectName: '',
  });
  const [error, setError] = useState('');
  const { login, loading } = useAuth();

  const handleInputChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');

    if (!formData.authUrl || !formData.username || !formData.password || !formData.projectName) {
      setError('Please fill in all fields');
      return;
    }

    try {
      const success = await login(
        formData.authUrl,
        formData.username,
        formData.password,
        formData.projectName
      );

      if (!success) {
        setError('Authentication failed. Please check your credentials.');
      }
    } catch (err) {
      setError('An error occurred during authentication.');
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <CloudIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
          <Typography component="h1" variant="h4" gutterBottom>
            OpenStack Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Sign in to your OpenStack environment
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              label="Authentication URL"
              placeholder="http://your-openstack-controller:5000/v3"
              value={formData.authUrl}
              onChange={handleInputChange('authUrl')}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              label="Username"
              placeholder="your-username"
              value={formData.username}
              onChange={handleInputChange('username')}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              label="Password"
              type="password"
              placeholder="your-password"
              value={formData.password}
              onChange={handleInputChange('password')}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              label="Project Name"
              placeholder="your-project"
              value={formData.projectName}
              onChange={handleInputChange('projectName')}
              disabled={loading}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
            This dashboard provides a modern web interface for managing your OpenStack resources.
            <br />
            Similar to Lens for Kubernetes, but designed for OpenStack environments.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
