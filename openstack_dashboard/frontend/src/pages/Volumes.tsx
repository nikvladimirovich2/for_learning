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

interface Volume {
  id: string;
  name: string;
  size: number;
  status: string;
  volume_type: string;
  attachments: any[];
}

const Volumes: React.FC = () => {
  const [volumes, setVolumes] = useState<Volume[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchVolumes();
  }, []);

  const fetchVolumes = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/volumes', { withCredentials: true });
      setVolumes(response.data);
    } catch (err) {
      setError('Failed to fetch volumes');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available':
        return 'success';
      case 'in-use':
        return 'info';
      case 'error':
        return 'error';
      default:
        return 'default';
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
        <Typography variant="h4">Volumes</Typography>
        <IconButton onClick={fetchVolumes}>
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
                <TableCell>Size (GB)</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Attachments</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {volumes.map((volume) => (
                <TableRow key={volume.id}>
                  <TableCell>{volume.name}</TableCell>
                  <TableCell>{volume.size}</TableCell>
                  <TableCell>
                    <Chip
                      label={volume.status}
                      color={getStatusColor(volume.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{volume.volume_type}</TableCell>
                  <TableCell>
                    {volume.attachments.length > 0 ? (
                      <Chip
                        label={`${volume.attachments.length} attached`}
                        color="info"
                        size="small"
                      />
                    ) : (
                      <Chip label="Not attached" color="default" size="small" />
                    )}
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

export default Volumes;
