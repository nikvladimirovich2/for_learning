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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import axios from 'axios';

interface Instance {
  id: string;
  name: string;
  status: string;
  flavor: string;
  image: string;
  created: string;
  networks: string[];
}

const Instances: React.FC = () => {
  const [instances, setInstances] = useState<Instance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    name: '',
    image_id: '',
    flavor_id: '',
    network_id: '',
  });

  useEffect(() => {
    fetchInstances();
  }, []);

  const fetchInstances = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/instances', { withCredentials: true });
      setInstances(response.data);
    } catch (err) {
      setError('Failed to fetch instances');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInstance = async () => {
    try {
      const response = await axios.post('/api/instances', createForm, { withCredentials: true });
      if (response.data.success) {
        setCreateDialogOpen(false);
        setCreateForm({ name: '', image_id: '', flavor_id: '', network_id: '' });
        fetchInstances();
      }
    } catch (err) {
      setError('Failed to create instance');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'ACTIVE':
        return 'success';
      case 'SHUTOFF':
        return 'warning';
      case 'ERROR':
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
        <Typography variant="h4">Instances</Typography>
        <Box>
          <IconButton onClick={fetchInstances} sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Instance
          </Button>
        </Box>
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
                <TableCell>Flavor</TableCell>
                <TableCell>Image</TableCell>
                <TableCell>Networks</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {instances.map((instance) => (
                <TableRow key={instance.id}>
                  <TableCell>{instance.name}</TableCell>
                  <TableCell>
                    <Chip
                      label={instance.status}
                      color={getStatusColor(instance.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{instance.flavor}</TableCell>
                  <TableCell>{instance.image}</TableCell>
                  <TableCell>
                    {instance.networks.map((network) => (
                      <Chip key={network} label={network} size="small" sx={{ mr: 0.5 }} />
                    ))}
                  </TableCell>
                  <TableCell>
                    {new Date(instance.created).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" sx={{ mr: 0.5 }}>
                      <PlayIcon />
                    </IconButton>
                    <IconButton size="small" sx={{ mr: 0.5 }}>
                      <StopIcon />
                    </IconButton>
                    <IconButton size="small" color="error">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create Instance Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Instance</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Instance Name"
            fullWidth
            variant="outlined"
            value={createForm.name}
            onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Image ID"
            fullWidth
            variant="outlined"
            value={createForm.image_id}
            onChange={(e) => setCreateForm({ ...createForm, image_id: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Flavor ID"
            fullWidth
            variant="outlined"
            value={createForm.flavor_id}
            onChange={(e) => setCreateForm({ ...createForm, flavor_id: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Network ID"
            fullWidth
            variant="outlined"
            value={createForm.network_id}
            onChange={(e) => setCreateForm({ ...createForm, network_id: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateInstance} variant="contained">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Instances;
