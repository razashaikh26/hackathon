import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  CreditCard,
  Refresh,
  Savings,
} from '@mui/icons-material';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';

// API Service
import { apiService, DashboardData, ExpenseData, FinancialOverview } from '../../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  BarElement
);

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [expenseData, setExpenseData] = useState<ExpenseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Get current user from localStorage
  const getCurrentUser = () => {
    try {
      const savedUser = localStorage.getItem('currentUser');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const currentUser = getCurrentUser();
      if (!currentUser) {
        throw new Error('No user found. Please login again.');
      }

      console.log('Fetching dashboard data for user:', currentUser.id);
      
      // Use database API endpoints instead of insights API
      try {
        // Fetch financial overview from database API
        const financialOverview = await apiService.getFinancialOverview(currentUser.id);
        console.log('Financial overview:', financialOverview);
        
        // Transform database data to dashboard format
        const dashboardData: DashboardData = {
          totalBalance: financialOverview.cash_balance || 0,
          monthlyIncome: 85000, // Default fallback value
          monthlyExpenses: financialOverview.expense_summary?.total || 0,
          savingsRate: 58.8, // Default fallback calculation
          portfolioValue: financialOverview.portfolio?.total_value || 0,
          portfolioGrowth: financialOverview.portfolio?.total_gain_loss_percentage || 0,
          currency: currentUser.currency_preference || 'INR',
          recentTransactions: financialOverview.recent_transactions || []
        };
        
        // Create expense data from the expense summary
        const expenseData: ExpenseData = {
          totalMonthly: financialOverview.expense_summary?.total || 0,
          currency: currentUser.currency_preference || 'INR',
          categories: financialOverview.expense_summary?.categories?.map((cat: any) => ({
            name: cat.category,
            amount: cat.amount,
            percentage: cat.percentage,
            currency: currentUser.currency_preference || 'INR'
          })) || []
        };
        
        setDashboardData(dashboardData);
        setExpenseData(expenseData);
        setLastUpdated(new Date());
        setError(null);
        
      } catch (apiError) {
        console.warn('Database API failed, using fallback data:', apiError);
        
        // Fallback to mock data if API fails
        const fallbackDashboard: DashboardData = {
          totalBalance: 925000.50,
          monthlyIncome: 85000.00,
          monthlyExpenses: 35000.00,
          savingsRate: 58.8,
          portfolioValue: 650000.00,
          portfolioGrowth: 15.2,
          currency: currentUser.currency_preference || 'INR',
          recentTransactions: [
            {
              id: '1',
              account_id: 'acc_1',
              amount: 85000,
              description: 'Salary Credit',
              category: 'Income',
              transaction_type: 'credit',
              transaction_date: new Date().toISOString(),
              currency: 'INR',
              created_at: new Date().toISOString()
            },
            {
              id: '2',
              account_id: 'acc_2',
              amount: -2500,
              description: 'Grocery Shopping',
              category: 'Food & Dining',
              transaction_type: 'debit',
              transaction_date: new Date(Date.now() - 86400000).toISOString(),
              currency: 'INR',
              created_at: new Date(Date.now() - 86400000).toISOString()
            },
            {
              id: '3',
              account_id: 'acc_3',
              amount: -15000,
              description: 'SIP Investment',
              category: 'Investment',
              transaction_type: 'debit',
              transaction_date: new Date(Date.now() - 172800000).toISOString(),
              currency: 'INR',
              created_at: new Date(Date.now() - 172800000).toISOString()
            }
          ]
        };
        
        const fallbackExpenses: ExpenseData = {
          totalMonthly: 35000,
          currency: 'INR',
          categories: [
            { name: 'Housing', amount: 15000, percentage: 42.9, currency: 'INR' },
            { name: 'Food & Dining', amount: 8000, percentage: 22.9, currency: 'INR' },
            { name: 'Transportation', amount: 4000, percentage: 11.4, currency: 'INR' },
            { name: 'Utilities', amount: 3000, percentage: 8.6, currency: 'INR' },
            { name: 'Entertainment', amount: 2500, percentage: 7.1, currency: 'INR' },
            { name: 'Healthcare', amount: 1500, percentage: 4.3, currency: 'INR' },
            { name: 'Other', amount: 1000, percentage: 2.9, currency: 'INR' }
          ]
        };
        
        setDashboardData(fallbackDashboard);
        setExpenseData(fallbackExpenses);
        setLastUpdated(new Date());
        setError(null);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Unable to load dashboard data. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number, currency: string = 'INR') => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || value === null || isNaN(value)) {
      return '0.0%';
    }
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading FinVoice Dashboard...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <IconButton onClick={fetchDashboardData} size="small">
          <Refresh />
        </IconButton>
      }>
        {error}
      </Alert>
    );
  }

  if (!dashboardData || !expenseData) {
    return (
      <Alert severity="warning">
        No dashboard data available. Please try refreshing.
      </Alert>
    );
  }

  // Calculate additional metrics
  const netSavings = dashboardData.monthlyIncome - dashboardData.monthlyExpenses;
  const savingsRate = dashboardData.savingsRate;

  // Chart configurations for expense breakdown
  const expenseBreakdownData = {
    labels: expenseData.categories.map(cat => cat.name),
    datasets: [
      {
        data: expenseData.categories.map(cat => cat.amount),
        backgroundColor: [
          '#FF6384', // Housing - Red
          '#36A2EB', // Food & Dining - Blue  
          '#FFCE56', // Transportation - Yellow
          '#4BC0C0', // Utilities - Teal
          '#9966FF', // Entertainment - Purple
          '#FF9F40', // Healthcare - Orange
          '#FF6384', // Other - Pink
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  // Recent transactions trend (mock for chart)
  const monthlyTrendData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Monthly Expenses (₹)',
        data: [32000, 35000, 33000, 36000, dashboardData.monthlyExpenses, 34000],
        borderColor: '#FF6384',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Monthly Income (₹)',
        data: [80000, 85000, 82000, 85000, dashboardData.monthlyIncome, 85000],
        borderColor: '#36A2EB',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        tension: 0.4,
      },
    ],
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          FinVoice Dashboard 
          <Chip 
            label="INR" 
            color="primary" 
            size="small" 
            sx={{ ml: 2 }}
          />
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Refresh data">
            <IconButton onClick={fetchDashboardData} size="small">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Balance
                  </Typography>
                  <Typography variant="h5" component="div">
                    {formatCurrency(dashboardData.totalBalance, dashboardData.currency)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Available funds
                  </Typography>
                </Box>
                <AccountBalance color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Portfolio Value
                  </Typography>
                  <Typography variant="h5" component="div">
                    {formatCurrency(dashboardData.portfolioValue, dashboardData.currency)}
                  </Typography>
                  <Box display="flex" alignItems="center">
                    {dashboardData.portfolioGrowth > 0 ? (
                      <TrendingUp color="success" fontSize="small" />
                    ) : (
                      <TrendingDown color="error" fontSize="small" />
                    )}
                    <Typography
                      variant="body2"
                      color={dashboardData.portfolioGrowth > 0 ? 'success.main' : 'error.main'}
                    >
                      {formatPercentage(dashboardData.portfolioGrowth)}
                    </Typography>
                  </Box>
                </Box>
                <TrendingUp color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Monthly Savings
                  </Typography>
                  <Typography variant="h5" component="div">
                    {formatCurrency(netSavings, dashboardData.currency)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Savings Rate: {savingsRate.toFixed(1)}%
                  </Typography>
                </Box>
                <Savings color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Monthly Expenses
                  </Typography>
                  <Typography variant="h5" component="div">
                    {formatCurrency(dashboardData.monthlyExpenses, dashboardData.currency)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Income: {formatCurrency(dashboardData.monthlyIncome, dashboardData.currency)}
                  </Typography>
                </Box>
                <CreditCard color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Income vs Expenses Trend
              </Typography>
              <Box height={300}>
                <Line
                  data={monthlyTrendData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top' as const,
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            return `${context.dataset.label}: ₹${context.parsed.y.toLocaleString('en-IN')}`;
                          }
                        }
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          callback: function(value) {
                            return '₹' + (value as number).toLocaleString('en-IN');
                          }
                        }
                      }
                    }
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Expense Breakdown
              </Typography>
              <Box height={300}>
                <Doughnut
                  data={expenseBreakdownData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom' as const,
                      },
                      tooltip: {
                        callbacks: {
                          label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = expenseData.totalMonthly;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ₹${value.toLocaleString('en-IN')} (${percentage}%)`;
                          }
                        }
                      }
                    },
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Transactions */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Transactions
          </Typography>
          <List>
            {dashboardData.recentTransactions.map((transaction, index) => (
              <React.Fragment key={transaction.id}>
                <ListItem>
                  <ListItemText
                    primary={transaction.description}
                    secondary={new Date(transaction.transaction_date).toLocaleDateString('en-IN')}
                  />
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip
                      label={transaction.transaction_type === 'credit' ? 'income' : 'expense'}
                      size="small"
                      color={
                        transaction.transaction_type === 'credit' ? 'success' : 'default'
                      }
                    />
                    <Typography
                      variant="body2"
                      color={
                        transaction.transaction_type === 'credit' ? 'success.main' : 'error.main'
                      }
                      fontWeight="bold"
                    >
                      {transaction.amount > 0 ? '+' : ''}
                      {formatCurrency(transaction.amount, transaction.currency)}
                    </Typography>
                  </Box>
                </ListItem>
                {index < dashboardData.recentTransactions.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Dashboard;
