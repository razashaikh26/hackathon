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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  TrackChanges as TargetIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface FinancialGoal {
  id: string;
  name: string;
  targetAmount: number;
  currentAmount: number;
  deadline: string;
  category: 'emergency' | 'retirement' | 'house' | 'vacation' | 'education' | 'debt' | 'investment' | 'other';
  priority: 'high' | 'medium' | 'low';
  status: 'active' | 'completed' | 'paused';
  monthlyContribution: number;
  description: string;
}

const goalCategories = [
  { value: 'emergency', label: 'Emergency Fund' },
  { value: 'retirement', label: 'Retirement' },
  { value: 'house', label: 'House/Property' },
  { value: 'vacation', label: 'Vacation' },
  { value: 'education', label: 'Education' },
  { value: 'debt', label: 'Debt Payoff' },
  { value: 'investment', label: 'Investment' },
  { value: 'other', label: 'Other' },
];

const Goals: React.FC = () => {
  const [goals, setGoals] = useState<FinancialGoal[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [newGoal, setNewGoal] = useState({
    name: '',
    targetAmount: '',
    deadline: '',
    category: 'other' as const,
    priority: 'medium' as const,
    monthlyContribution: '',
    description: ''
  });

  useEffect(() => {
    // Mock data loading
    setTimeout(() => {
      setGoals([
        {
          id: '1',
          name: 'Emergency Fund',
          targetAmount: 10000,
          currentAmount: 6500,
          deadline: '2025-12-31',
          category: 'emergency',
          priority: 'high',
          status: 'active',
          monthlyContribution: 500,
          description: 'Build emergency fund for 6 months of expenses'
        },
        {
          id: '2',
          name: 'House Down Payment',
          targetAmount: 50000,
          currentAmount: 25000,
          deadline: '2026-06-30',
          category: 'house',
          priority: 'high',
          status: 'active',
          monthlyContribution: 1500,
          description: 'Save for house down payment'
        },
        {
          id: '3',
          name: 'Vacation to Europe',
          targetAmount: 8000,
          currentAmount: 3200,
          deadline: '2025-07-01',
          category: 'vacation',
          priority: 'medium',
          status: 'active',
          monthlyContribution: 400,
          description: 'Two-week European vacation'
        },
        {
          id: '4',
          name: 'Retirement Fund',
          targetAmount: 500000,
          currentAmount: 150000,
          deadline: '2045-12-31',
          category: 'retirement',
          priority: 'high',
          status: 'active',
          monthlyContribution: 800,
          description: 'Long-term retirement savings'
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAddGoal = () => {
    const goal: FinancialGoal = {
      id: Date.now().toString(),
      name: newGoal.name,
      targetAmount: parseFloat(newGoal.targetAmount),
      currentAmount: 0,
      deadline: newGoal.deadline,
      category: newGoal.category,
      priority: newGoal.priority,
      status: 'active',
      monthlyContribution: parseFloat(newGoal.monthlyContribution),
      description: newGoal.description
    };

    setGoals([...goals, goal]);
    setNewGoal({
      name: '',
      targetAmount: '',
      deadline: '',
      category: 'other',
      priority: 'medium',
      monthlyContribution: '',
      description: ''
    });
    setOpenDialog(false);
  };

  const getProgressPercentage = (goal: FinancialGoal) => {
    return Math.min((goal.currentAmount / goal.targetAmount) * 100, 100);
  };

  const getMonthsToDeadline = (deadline: string) => {
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const monthsDiff = (deadlineDate.getFullYear() - now.getFullYear()) * 12 + 
                       (deadlineDate.getMonth() - now.getMonth());
    return Math.max(monthsDiff, 0);
  };

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: 'primary' | 'secondary' | 'success' | 'warning' | 'info' | 'error' } = {
      emergency: 'error',
      retirement: 'primary',
      house: 'success',
      vacation: 'warning',
      education: 'info',
      debt: 'error',
      investment: 'primary',
      other: 'secondary'
    };
    return colors[category] || 'secondary';
  };

  const getPriorityColor = (priority: string) => {
    const colors: { [key: string]: 'error' | 'warning' | 'success' } = {
      high: 'error',
      medium: 'warning',
      low: 'success'
    };
    return colors[priority] || 'success';
  };

  const totalTargetAmount = goals.reduce((sum, goal) => sum + goal.targetAmount, 0);
  const totalCurrentAmount = goals.reduce((sum, goal) => sum + goal.currentAmount, 0);
  const totalMonthlyContribution = goals.reduce((sum, goal) => sum + goal.monthlyContribution, 0);
  const activeGoals = goals.filter(goal => goal.status === 'active');
  const completedGoals = goals.filter(goal => goal.status === 'completed');

  const progressData = goals.map(goal => ({
    name: goal.name,
    progress: getProgressPercentage(goal),
    target: goal.targetAmount,
    current: goal.currentAmount
  }));

  const categoryData = goalCategories.map(category => {
    const categoryGoals = goals.filter(goal => goal.category === category.value);
    const totalTarget = categoryGoals.reduce((sum, goal) => sum + goal.targetAmount, 0);
    const totalCurrent = categoryGoals.reduce((sum, goal) => sum + goal.currentAmount, 0);
    return {
      category: category.label,
      target: totalTarget,
      current: totalCurrent,
      count: categoryGoals.length
    };
  }).filter(item => item.count > 0);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Financial Goals
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
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

      <Alert severity="info" sx={{ mb: 3 }}>
        You're on track to achieve {activeGoals.length} active goals with a total monthly contribution of ${totalMonthlyContribution.toLocaleString()}
      </Alert>

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" icon={<TargetIcon />} />
        <Tab label="Active Goals" icon={<TimelineIcon />} />
        <Tab label="Progress Analysis" icon={<TrendingUpIcon />} />
      </Tabs>

      {tabValue === 0 && (
        <>
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TargetIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Total Target</Typography>
                  </Box>
                  <Typography variant="h4" color="primary">
                    ${totalTargetAmount.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Across {goals.length} goals
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6">Current Saved</Typography>
                  </Box>
                  <Typography variant="h4" color="success.main">
                    ${totalCurrentAmount.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {((totalCurrentAmount / totalTargetAmount) * 100).toFixed(1)}% of target
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <TimelineIcon color="warning" sx={{ mr: 1 }} />
                    <Typography variant="h6">Monthly Savings</Typography>
                  </Box>
                  <Typography variant="h4" color="warning.main">
                    ${totalMonthlyContribution.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total monthly contributions
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6">Completed</Typography>
                  </Box>
                  <Typography variant="h4" color="success.main">
                    {completedGoals.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Goals achieved
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Goal Progress Overview
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={progressData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="progress" fill="#8884d8" name="Progress %" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Goals by Category
                  </Typography>
                  <List>
                    {categoryData.map((category) => (
                      <ListItem key={category.category}>
                        <ListItemText
                          primary={category.category}
                          secondary={`${category.count} goal(s)`}
                        />
                        <ListItemSecondaryAction>
                          <Typography variant="body2">
                            ${category.current.toLocaleString()} / ${category.target.toLocaleString()}
                          </Typography>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}

      {tabValue === 1 && (
        <Grid container spacing={3}>
          {activeGoals.map((goal) => {
            const progress = getProgressPercentage(goal);
            const monthsLeft = getMonthsToDeadline(goal.deadline);
            
            return (
              <Grid item xs={12} md={6} lg={4} key={goal.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        {goal.name}
                      </Typography>
                      <Box>
                        <IconButton size="small">
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="error">
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Chip 
                        label={goalCategories.find(c => c.value === goal.category)?.label} 
                        color={getCategoryColor(goal.category)} 
                        size="small" 
                        sx={{ mr: 1 }}
                      />
                      <Chip 
                        label={`${goal.priority} priority`} 
                        color={getPriorityColor(goal.priority)} 
                        size="small" 
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {goal.description}
                    </Typography>

                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">
                          ${goal.currentAmount.toLocaleString()} of ${goal.targetAmount.toLocaleString()}
                        </Typography>
                        <Typography variant="body2">
                          {progress.toFixed(1)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={progress}
                        color={progress >= 100 ? 'success' : progress >= 75 ? 'primary' : progress >= 50 ? 'warning' : 'error'}
                      />
                    </Box>

                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Monthly: ${goal.monthlyContribution.toLocaleString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          {monthsLeft} months left
                        </Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary">
                          Deadline: {new Date(goal.deadline).toLocaleDateString()}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Savings Progress Timeline
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart
                    data={goals.map((goal, index) => ({
                      name: goal.name,
                      target: goal.targetAmount,
                      current: goal.currentAmount,
                      progress: getProgressPercentage(goal)
                    }))}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [
                      name === 'progress' ? `${value}%` : `$${value.toLocaleString()}`, 
                      name === 'progress' ? 'Progress' : name === 'target' ? 'Target' : 'Current'
                    ]} />
                    <Legend />
                    <Line type="monotone" dataKey="current" stroke="#8884d8" name="Current Amount" />
                    <Line type="monotone" dataKey="target" stroke="#82ca9d" name="Target Amount" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Priority Distribution
                </Typography>
                <Box>
                  {['high', 'medium', 'low'].map(priority => {
                    const priorityGoals = goals.filter(goal => goal.priority === priority);
                    const priorityAmount = priorityGoals.reduce((sum, goal) => sum + goal.targetAmount, 0);
                    const percentage = (priorityAmount / totalTargetAmount) * 100;
                    
                    return (
                      <Box key={priority} sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                            {priority} Priority ({priorityGoals.length} goals)
                          </Typography>
                          <Typography variant="body2">
                            {percentage.toFixed(1)}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={percentage}
                          color={getPriorityColor(priority)}
                        />
                      </Box>
                    );
                  })}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Achievement Timeline
                </Typography>
                <List>
                  {goals.sort((a, b) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime()).map((goal) => {
                    const monthsLeft = getMonthsToDeadline(goal.deadline);
                    const onTrack = goal.currentAmount + (goal.monthlyContribution * monthsLeft) >= goal.targetAmount;
                    
                    return (
                      <ListItem key={goal.id}>
                        <ListItemText
                          primary={goal.name}
                          secondary={`Due: ${new Date(goal.deadline).toLocaleDateString()}`}
                        />
                        <ListItemSecondaryAction>
                          <Chip
                            label={onTrack ? 'On Track' : 'Behind'}
                            color={onTrack ? 'success' : 'warning'}
                            size="small"
                          />
                        </ListItemSecondaryAction>
                      </ListItem>
                    );
                  })}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Add Goal Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Financial Goal</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Goal Name"
                value={newGoal.name}
                onChange={(e) => setNewGoal({ ...newGoal, name: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Target Amount"
                type="number"
                value={newGoal.targetAmount}
                onChange={(e) => setNewGoal({ ...newGoal, targetAmount: e.target.value })}
                InputProps={{ startAdornment: '$' }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Monthly Contribution"
                type="number"
                value={newGoal.monthlyContribution}
                onChange={(e) => setNewGoal({ ...newGoal, monthlyContribution: e.target.value })}
                InputProps={{ startAdornment: '$' }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Category"
                select
                value={newGoal.category}
                onChange={(e) => setNewGoal({ ...newGoal, category: e.target.value as any })}
              >
                {goalCategories.map((category) => (
                  <MenuItem key={category.value} value={category.value}>
                    {category.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Priority"
                select
                value={newGoal.priority}
                onChange={(e) => setNewGoal({ ...newGoal, priority: e.target.value as any })}
              >
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target Date"
                type="date"
                value={newGoal.deadline}
                onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={newGoal.description}
                onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAddGoal}
            variant="contained"
            disabled={!newGoal.name || !newGoal.targetAmount || !newGoal.deadline}
          >
            Add Goal
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Goals;
