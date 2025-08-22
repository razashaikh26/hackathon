import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  LinearProgress,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  TrackChanges as TargetIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

// API Service
import { apiService, Goal } from '../../services/api';

interface FinancialGoal {
  id: string;
  user_id: string;
  goal_name: string;
  goal_type: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  monthly_contribution: number;
  priority: string;
  is_active: boolean;
  progress_percentage: number;
  months_remaining: number;
  required_monthly_amount: number;
  currency: string;
  created_at: string;
}

const goalTypes = [
  'Emergency Fund',
  'Retirement',
  'House Purchase', 
  'Vacation',
  'Education',
  'Debt Payoff',
  'Investment',
  'Car Purchase',
  'Wedding',
  'Other'
];

const priorities = [
  'high',
  'medium',
  'low'
];

const Goals: React.FC = () => {
  // Helper function to safely handle number formatting
  const safeNumber = (value: number | undefined | null): number => {
    return typeof value === 'number' && !isNaN(value) ? value : 0;
  };

  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingGoal, setEditingGoal] = useState<FinancialGoal | null>(null);
  const [goals, setGoals] = useState<FinancialGoal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newGoal, setNewGoal] = useState({
    goal_name: '',
    goal_type: '',
    target_amount: '',
    target_date: '',
    monthly_contribution: '',
    priority: 'medium'
  });

  useEffect(() => {
    fetchGoals();
  }, []);

  // Get current user from localStorage
  const getCurrentUser = () => {
    try {
      const savedUser = localStorage.getItem('currentUser');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  };

  const fetchGoals = async () => {
    setLoading(true);
    setError(null);
    try {
      const user = getCurrentUser();
      if (!user) {
        throw new Error('No user found. Please login again.');
      }

      // Fetch user goals from database
      const userGoals = await apiService.getUserGoals(user.id);
      setGoals(userGoals);

    } catch (error) {
      console.error('Error fetching goals:', error);
      setError('Unable to load goals data. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddGoal = async () => {
    try {
      const user = getCurrentUser();
      if (!user) {
        throw new Error('User not found');
      }

      const goalData = {
        name: newGoal.goal_name, // Send 'name' to backend
        goal_type: newGoal.goal_type,
        target_amount: parseFloat(newGoal.target_amount),
        target_date: newGoal.target_date,
        monthly_contribution: parseFloat(newGoal.monthly_contribution) || 0,
        priority: newGoal.priority,
        currency: user.currency_preference || 'INR'
      };

      await apiService.createGoal(user.id, goalData);

      setOpenDialog(false);
      setNewGoal({
        goal_name: '',
        goal_type: '',
        target_amount: '',
        target_date: '',
        monthly_contribution: '',
        priority: 'medium'
      });

      // Refresh data
      await fetchGoals();

    } catch (error) {
      console.error('Error adding goal:', error);
      setError('Failed to add goal. Please try again.');
    }
  };

  const handleEditGoal = (goal: FinancialGoal) => {
    setEditingGoal(goal);
    setNewGoal({
      goal_name: goal.goal_name,
      goal_type: goal.goal_type,
      target_amount: goal.target_amount.toString(),
      target_date: goal.target_date.split('T')[0], // Format date for input
      monthly_contribution: goal.monthly_contribution.toString(),
      priority: goal.priority
    });
    setOpenEditDialog(true);
  };

  const handleUpdateGoal = async () => {
    try {
      if (!editingGoal) {
        throw new Error('No goal selected for editing');
      }

      const goalData = {
        name: newGoal.goal_name, // Send 'name' to backend
        goal_type: newGoal.goal_type,
        target_amount: parseFloat(newGoal.target_amount),
        target_date: newGoal.target_date,
        monthly_contribution: parseFloat(newGoal.monthly_contribution) || 0,
        priority: newGoal.priority
      };

      await apiService.updateGoal(editingGoal.id, goalData);

      setOpenEditDialog(false);
      setEditingGoal(null);
      setNewGoal({
        goal_name: '',
        goal_type: '',
        target_amount: '',
        target_date: '',
        monthly_contribution: '',
        priority: 'medium'
      });

      // Refresh data
      await fetchGoals();

    } catch (error) {
      console.error('Error updating goal:', error);
      setError('Failed to update goal. Please try again.');
    }
  };

  const handleDeleteGoal = async (goalId: string) => {
    if (!window.confirm('Are you sure you want to delete this goal?')) {
      return;
    }

    try {
      await apiService.deleteGoal(goalId);
      
      // Refresh data
      await fetchGoals();
      
    } catch (error) {
      console.error('Error deleting goal:', error);
      setError('Failed to delete goal. Please try again.');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 50) return 'primary';
    if (percentage >= 25) return 'warning';
    return 'error';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={fetchGoals} startIcon={<RefreshIcon />}>
          Retry
        </Button>
      </Box>
    );
  }

  const activeGoals = goals.filter(g => g.is_active);
  const completedGoals = goals.filter(g => safeNumber(g.progress_percentage) >= 100);
  const totalTargetAmount = activeGoals.reduce((sum, g) => sum + g.target_amount, 0);
  const totalCurrentAmount = activeGoals.reduce((sum, g) => sum + g.current_amount, 0);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Financial Goals
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Add Goal
        </Button>
      </Box>

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="All Goals" />
        <Tab label="Progress Tracking" />
      </Tabs>

      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Summary Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TargetIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Active Goals
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {activeGoals.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Completed Goals
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {completedGoals.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingUpIcon color="info" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Target
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {formatCurrency(totalTargetAmount)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TimelineIcon color="secondary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Saved
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold" color="secondary.main">
                  {formatCurrency(totalCurrentAmount)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Active Goals List */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Active Goals Progress
                </Typography>
                {activeGoals.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
                    No active goals found. Create your first financial goal to get started!
                  </Typography>
                ) : (
                  <Grid container spacing={2}>
                    {activeGoals.map((goal) => (
                      <Grid item xs={12} md={6} key={goal.id}>
                        <Card variant="outlined">
                          <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                              <Typography variant="h6">{goal.goal_name}</Typography>
                              <Chip 
                                label={goal.priority} 
                                size="small" 
                                color={getPriorityColor(goal.priority) as any}
                              />
                            </Box>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              {goal.goal_type}
                            </Typography>
                            <Box sx={{ mb: 2 }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2">
                                  {formatCurrency(goal.current_amount)} of {formatCurrency(goal.target_amount)}
                                </Typography>
                                <Typography variant="body2">
                                  {safeNumber(goal.progress_percentage).toFixed(1)}%
                                </Typography>
                              </Box>
                              <LinearProgress
                                variant="determinate"
                                value={Math.min(safeNumber(goal.progress_percentage), 100)}
                                color={getProgressColor(safeNumber(goal.progress_percentage)) as any}
                              />
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              Target Date: {new Date(goal.target_date).toLocaleDateString()}
                            </Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                              <IconButton size="small" onClick={() => handleEditGoal(goal)}>
                                <EditIcon />
                              </IconButton>
                              <IconButton size="small" color="error" onClick={() => handleDeleteGoal(goal.id)}>
                                <DeleteIcon />
                              </IconButton>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              All Goals
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Goal Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Target Amount</TableCell>
                    <TableCell align="right">Current Amount</TableCell>
                    <TableCell align="center">Progress</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Target Date</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {goals.map((goal) => (
                    <TableRow key={goal.id}>
                      <TableCell>{goal.goal_name}</TableCell>
                      <TableCell>
                        <Chip label={goal.goal_type} size="small" />
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(goal.target_amount)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(goal.current_amount)}
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Box sx={{ width: '100%', mr: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={Math.min(safeNumber(goal.progress_percentage), 100)}
                              color={getProgressColor(safeNumber(goal.progress_percentage)) as any}
                            />
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            {safeNumber(goal.progress_percentage).toFixed(1)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={goal.priority} 
                          size="small" 
                          color={getPriorityColor(goal.priority) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(goal.target_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="center">
                        <IconButton size="small" onClick={() => handleEditGoal(goal)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDeleteGoal(goal.id)}>
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {goals.length === 0 && (
              <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
                No goals found. Create your first financial goal to get started!
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      {/* Add Goal Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Goal</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Goal Name"
              value={newGoal.goal_name}
              onChange={(e) => setNewGoal({ ...newGoal, goal_name: e.target.value })}
              fullWidth
              required
              placeholder="e.g., Emergency Fund"
            />
            <TextField
              select
              label="Goal Type"
              value={newGoal.goal_type}
              onChange={(e) => setNewGoal({ ...newGoal, goal_type: e.target.value })}
              fullWidth
              required
            >
              {goalTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Target Amount"
              type="number"
              value={newGoal.target_amount}
              onChange={(e) => setNewGoal({ ...newGoal, target_amount: e.target.value })}
              fullWidth
              required
              placeholder="100000"
            />
            <TextField
              label="Target Date"
              type="date"
              value={newGoal.target_date}
              onChange={(e) => setNewGoal({ ...newGoal, target_date: e.target.value })}
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Monthly Contribution"
              type="number"
              value={newGoal.monthly_contribution}
              onChange={(e) => setNewGoal({ ...newGoal, monthly_contribution: e.target.value })}
              fullWidth
              placeholder="5000"
            />
            <TextField
              select
              label="Priority"
              value={newGoal.priority}
              onChange={(e) => setNewGoal({ ...newGoal, priority: e.target.value })}
              fullWidth
              required
            >
              {priorities.map((priority) => (
                <MenuItem key={priority} value={priority}>
                  {priority.charAt(0).toUpperCase() + priority.slice(1)}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleAddGoal}
            disabled={!newGoal.goal_name || !newGoal.goal_type || !newGoal.target_amount || !newGoal.target_date}
          >
            Add Goal
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Goal Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Goal</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Goal Name"
              value={newGoal.goal_name}
              onChange={(e) => setNewGoal({ ...newGoal, goal_name: e.target.value })}
              fullWidth
              required
            />
            <TextField
              select
              label="Goal Type"
              value={newGoal.goal_type}
              onChange={(e) => setNewGoal({ ...newGoal, goal_type: e.target.value })}
              fullWidth
              required
            >
              {goalTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Target Amount"
              type="number"
              value={newGoal.target_amount}
              onChange={(e) => setNewGoal({ ...newGoal, target_amount: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Target Date"
              type="date"
              value={newGoal.target_date}
              onChange={(e) => setNewGoal({ ...newGoal, target_date: e.target.value })}
              fullWidth
              required
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Monthly Contribution"
              type="number"
              value={newGoal.monthly_contribution}
              onChange={(e) => setNewGoal({ ...newGoal, monthly_contribution: e.target.value })}
              fullWidth
            />
            <TextField
              select
              label="Priority"
              value={newGoal.priority}
              onChange={(e) => setNewGoal({ ...newGoal, priority: e.target.value })}
              fullWidth
              required
            >
              {priorities.map((priority) => (
                <MenuItem key={priority} value={priority}>
                  {priority.charAt(0).toUpperCase() + priority.slice(1)}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleUpdateGoal}
            disabled={!newGoal.goal_name || !newGoal.goal_type || !newGoal.target_amount || !newGoal.target_date}
          >
            Update Goal
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Goals;
