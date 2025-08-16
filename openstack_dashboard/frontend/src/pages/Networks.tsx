import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import axios from 'axios';

interface Network {
  id: string;
  name: string;
  status: string;
  admin_state_up: boolean;
  shared: boolean;
  subnets: string[];
}

const Networks: React.FC = () => {
  const [networks, setNetworks] = useState<Network[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchNetworks();
  }, []);

  const fetchNetworks = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/networks', { withCredentials: true });
      setNetworks(response.data);
    } catch (err) {
      setError('Failed to fetch networks');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Networks</Typography>
        <IconButton onClick={fetchNetworks}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Admin State</TableCell>
                <TableCell>Shared</TableCell>
                <TableCell>Subnets</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {networks.map((network) => (
                <TableRow key={network.id}>
                  <TableCell>{network.name}</TableCell>
                  <TableCell>
                    <Chip
                      label={network.status}
                      color={network.status === 'ACTIVE' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={network.admin_state_up ? 'UP' : 'DOWN'}
                      color={network.admin_state_up ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={network.shared ? 'Yes' : 'No'}
                      color={network.shared ? 'info' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {network.subnets.map((subnet) => (
                      <Chip key={subnet} label={subnet} size="small" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                  <TableCell>
                    <IconButton size="small">
                      <ViewIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default Networks;
