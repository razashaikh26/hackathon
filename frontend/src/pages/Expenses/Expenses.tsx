import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  LinearProgress,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  IconButton,
  Tooltip as MuiTooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  Receipt as ReceiptIcon,
  Category as CategoryIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

// API Service
import { apiService, ExpenseData } from '../../services/api';

interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  category: string;
  merchant: string;
  account: string;
  account_id: string;
  transaction_type: 'debit' | 'credit';
  transaction_date: string;
  currency: string;
  created_at: string;
  isAnomaly?: boolean;
}

interface CategoryBudget {
  category: string;
  budgeted: number;
  spent: number;
  remaining: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const categories = [
  'Food & Dining',
  'Transportation',
  'Shopping',
  'Entertainment',
  'Bills & Utilities',
  'Healthcare',
  'Travel',
  'Education',
  'Groceries',
  'Gas & Fuel',
  'Insurance',
  'Rent/Mortgage',
  'Personal Care',
  'Gifts & Donations',
  'Investment',
  'Savings',
  'Other'
];

const Expenses: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<any>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [categoryBudgets, setCategoryBudgets] = useState<CategoryBudget[]>([]);
  const [expenseData, setExpenseData] = useState<ExpenseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newTransaction, setNewTransaction] = useState({
    description: '',
    amount: '',
    category: '',
    account_id: '',
    merchant: '',
    account: '',
    transaction_type: 'debit' as 'debit' | 'credit'
  });

  useEffect(() => {
    fetchExpenseData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  const fetchExpenseData = async () => {
    setLoading(true);
    setError(null);
    try {
      const user = getCurrentUser();
      if (!user) {
        throw new Error('No user found. Please login again.');
      }

      // Fetch user accounts and transactions from database
      const [userAccounts, userTransactions] = await Promise.all([
        apiService.getUserAccounts(user.id),
        apiService.getUserTransactions(user.id)
      ]);

      setAccounts(userAccounts);

      // Transform API transactions to local format
      const transformedTransactions: Transaction[] = userTransactions.map(t => ({
        id: t.id,
        date: new Date(t.transaction_date).toLocaleDateString(),
        description: t.description,
        amount: t.amount,
        category: t.category,
        merchant: t.description, // Use description as merchant for now
        account: userAccounts.find(acc => acc.id === t.account_id)?.account_name || 'Unknown',
        account_id: t.account_id,
        transaction_type: t.transaction_type,
        transaction_date: t.transaction_date,
        currency: t.currency,
        created_at: t.created_at,
        isAnomaly: Math.abs(t.amount) > 5000 // Mark large transactions as anomalies
      }));

      setTransactions(transformedTransactions);

      // Calculate expense data from transactions
      const expenseTransactions = transformedTransactions.filter(t => t.transaction_type === 'debit');
      const totalExpenses = expenseTransactions.reduce((sum, t) => sum + Math.abs(t.amount), 0);
      
      // Group by category
      const categoryMap = new Map();
      expenseTransactions.forEach(t => {
        const current = categoryMap.get(t.category) || 0;
        categoryMap.set(t.category, current + Math.abs(t.amount));
      });

      const expenseCategories = Array.from(categoryMap.entries()).map(([name, amount]) => ({
        name,
        amount,
        percentage: totalExpenses > 0 ? (amount / totalExpenses) * 100 : 0,
        currency: user.currency_preference || 'INR'
      }));

      setExpenseData({
        totalMonthly: totalExpenses,
        currency: user.currency_preference || 'INR',
        categories: expenseCategories
      });

      // Create category budgets
      const budgets: CategoryBudget[] = expenseCategories.map(cat => ({
        category: cat.name,
        budgeted: cat.amount * 1.2, // Set budget 20% higher than current spend
        spent: cat.amount,
        remaining: (cat.amount * 1.2) - cat.amount
      }));

      setCategoryBudgets(budgets);

    } catch (error) {
      console.error('Error fetching expense data:', error);
      setError('Unable to load expense data. Please check if the backend is running.');
      
      // Fallback to demo data
      setExpenseData({
        totalMonthly: 45000,
        currency: 'INR',
        categories: [
          { name: 'Food & Dining', amount: 15000, percentage: 33.3, currency: 'INR' },
          { name: 'Transportation', amount: 8000, percentage: 17.8, currency: 'INR' },
          { name: 'Shopping', amount: 12000, percentage: 26.7, currency: 'INR' },
          { name: 'Entertainment', amount: 5000, percentage: 11.1, currency: 'INR' },
          { name: 'Bills & Utilities', amount: 5000, percentage: 11.1, currency: 'INR' }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAddTransaction = async () => {
    try {
      const user = getCurrentUser();
      if (!user) {
        setError('User not found. Please login again.');
        return;
      }

      // Enhanced validation
      if (!newTransaction.description.trim()) {
        setError('Please enter a transaction description');
        return;
      }

      if (!newTransaction.amount || parseFloat(newTransaction.amount) <= 0) {
        setError('Please enter a valid amount greater than 0');
        return;
      }

      if (!newTransaction.category) {
        setError('Please select a category');
        return;
      }

      if (!newTransaction.account_id) {
        setError('Please select an account');
        return;
      }

      setError(null); // Clear any previous errors

      const transactionData = {
        account_id: newTransaction.account_id,
        amount: newTransaction.transaction_type === 'debit' 
          ? -Math.abs(parseFloat(newTransaction.amount))
          : Math.abs(parseFloat(newTransaction.amount)),
        description: newTransaction.description.trim(),
        category: newTransaction.category,
        transaction_type: newTransaction.transaction_type,
        currency: user.currency_preference || 'INR'
      };

      console.log('Creating transaction:', transactionData);
      await apiService.createTransaction(transactionData);

      // Success feedback
      setOpenDialog(false);
      setNewTransaction({
        description: '',
        amount: '',
        category: '',
        account_id: '',
        merchant: '',
        account: '',
        transaction_type: 'debit'
      });

      // Show success message
      setError('Transaction added successfully!');
      setTimeout(() => setError(null), 3000);

      // Refresh data
      await fetchExpenseData();

    } catch (error) {
      console.error('Error adding transaction:', error);
      setError('Failed to add transaction. Please check your internet connection and try again.');
    }
  };

  const handleEditTransaction = (transaction: Transaction) => {
    setEditingTransaction(transaction);
    setNewTransaction({
      description: transaction.description,
      amount: Math.abs(transaction.amount).toString(),
      category: transaction.category,
      account_id: transaction.account_id,
      merchant: transaction.merchant,
      account: transaction.account,
      transaction_type: transaction.transaction_type
    });
    setOpenEditDialog(true);
  };

  const handleUpdateTransaction = async () => {
    try {
      if (!editingTransaction) {
        throw new Error('No transaction selected for editing');
      }

      const user = getCurrentUser();
      if (!user) {
        throw new Error('User not found');
      }

      const transactionData = {
        amount: newTransaction.transaction_type === 'debit' 
          ? -Math.abs(parseFloat(newTransaction.amount))
          : Math.abs(parseFloat(newTransaction.amount)),
        description: newTransaction.description,
        category: newTransaction.category,
        transaction_type: newTransaction.transaction_type
      };

      await apiService.updateTransaction(editingTransaction.id, transactionData);

      setOpenEditDialog(false);
      setEditingTransaction(null);
      setNewTransaction({
        description: '',
        amount: '',
        category: '',
        account_id: '',
        merchant: '',
        account: '',
        transaction_type: 'debit'
      });

      // Refresh data
      await fetchExpenseData();

    } catch (error) {
      console.error('Error updating transaction:', error);
      setError('Failed to update transaction. Please try again.');
    }
  };

  const handleDeleteTransaction = async (transactionId: string) => {
    if (!window.confirm('Are you sure you want to delete this transaction?')) {
      return;
    }

    try {
      await apiService.deleteTransaction(transactionId);
      
      // Refresh data
      await fetchExpenseData();
      
    } catch (error) {
      console.error('Error deleting transaction:', error);
      setError('Failed to delete transaction. Please try again.');
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

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Expenses
        </Typography>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Loading expense data...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error && !expenseData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" action={
          <IconButton onClick={fetchExpenseData} size="small">
            <RefreshIcon />
          </IconButton>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  const categoryData = expenseData ? expenseData.categories.map(cat => ({
    name: cat.name,
    value: cat.amount
  })) : [];

  const monthlySpending = [
    { month: 'Jan', amount: 42000 },
    { month: 'Feb', amount: 38000 },
    { month: 'Mar', amount: 44000 },
    { month: 'Apr', amount: 41000 },
    { month: 'May', amount: 46000 },
    { month: 'Jun', amount: 43000 },
    { month: 'Jul', amount: 45000 },
    { month: 'Aug', amount: expenseData?.totalMonthly || 45000 }
  ];

  const totalSpent = expenseData?.totalMonthly || 0;
  const anomalies = transactions.filter(t => t.isAnomaly);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Expenses
          <Chip 
            label="INR" 
            color="primary" 
            size="small" 
            sx={{ ml: 2 }}
          />
        </Typography>
        <Box display="flex" gap={1}>
          <MuiTooltip title="Refresh data">
            <IconButton onClick={fetchExpenseData} size="small">
              <RefreshIcon />
            </IconButton>
          </MuiTooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
            disabled={accounts.length === 0}
          >
            Add Transaction
          </Button>
        </Box>
      </Box>

      {error && error.includes('successfully') ? (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      ) : error ? (
        <Alert severity="warning" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      ) : null}

      {accounts.length === 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          No accounts found. Please create an account first to add transactions.
        </Alert>
      )}

      {anomalies.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }} icon={<WarningIcon />}>
          {anomalies.length} unusual transaction{anomalies.length > 1 ? 's' : ''} detected this month
        </Alert>
      )}

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Transactions" />
        <Tab label="Budget Analysis" />
        <Tab label="Trends" />
      </Tabs>

      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <ReceiptIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Total Spent</Typography>
                </Box>
                <Typography variant="h4" color="error">
                  {formatCurrency(totalSpent)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  This month
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <CategoryIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Categories</Typography>
                </Box>
                <Typography variant="h4">
                  {categoryData.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active categories
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingDownIcon color="error" sx={{ mr: 1 }} />
                  <Typography variant="h6">vs Last Month</Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  -12.3%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ₹5,500 less spent
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <WarningIcon color="warning" sx={{ mr: 1 }} />
                  <Typography variant="h6">Anomalies</Typography>
                </Box>
                <Typography variant="h4" color="warning.main">
                  {anomalies.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Unusual transactions
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Spending by Category
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [formatCurrency(value as number), 'Amount']} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Monthly Trend
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={monthlySpending}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis tickFormatter={(value) => `₹${(value/1000).toFixed(0)}k`} />
                    <Tooltip formatter={(value) => [formatCurrency(value as number), 'Spent']} />
                    <Line type="monotone" dataKey="amount" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Transactions
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Merchant</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell>{new Date(transaction.date).toLocaleDateString('en-IN')}</TableCell>
                      <TableCell>{transaction.description}</TableCell>
                      <TableCell>
                        <Chip label={transaction.category} size="small" />
                      </TableCell>
                      <TableCell>{transaction.merchant}</TableCell>
                      <TableCell align="right" sx={{ color: 'error.main', fontWeight: 'bold' }}>
                        {formatCurrency(Math.abs(transaction.amount))}
                      </TableCell>
                      <TableCell>
                        {transaction.isAnomaly ? (
                          <Chip label="Anomaly" color="warning" size="small" />
                        ) : (
                          <Chip label="Normal" color="success" size="small" />
                        )}
                      </TableCell>
                      <TableCell align="center">
                        <IconButton size="small" onClick={() => handleEditTransaction(transaction)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDeleteTransaction(transaction.id)}>
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {transactions.length === 0 && (
              <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
                No transactions found. Add your first expense to get started!
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      {tabValue === 2 && (
        <Grid container spacing={3}>
          {categoryBudgets.map((budget) => (
            <Grid item xs={12} md={6} lg={4} key={budget.category}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {budget.category}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">
                        {formatCurrency(budget.spent || 0)} of {formatCurrency(budget.budgeted || 0)}
                      </Typography>
                      <Typography variant="body2">
                        {budget.budgeted > 0 ? ((budget.spent / budget.budgeted) * 100).toFixed(0) : '0'}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={budget.budgeted > 0 ? Math.min((budget.spent / budget.budgeted) * 100, 100) : 0}
                      color={budget.remaining < 0 ? 'error' : budget.remaining < budget.budgeted * 0.2 ? 'warning' : 'primary'}
                    />
                  </Box>
                  <Typography
                    variant="body2"
                    color={budget.remaining < 0 ? 'error' : 'text.secondary'}
                  >
                    {budget.remaining < 0 ? 'Over budget by' : 'Remaining:'} {formatCurrency(Math.abs(budget.remaining || 0))}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {tabValue === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Spending Trends
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={monthlySpending}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(value) => `₹${(value/1000).toFixed(0)}k`} />
                <Tooltip formatter={(value) => [formatCurrency(value as number), 'Spent']} />
                <Legend />
                <Bar dataKey="amount" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Add Transaction Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Transaction</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Description"
              value={newTransaction.description}
              onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
              fullWidth
              required
              placeholder="e.g., Dinner at restaurant"
            />
            <TextField
              label="Amount"
              type="number"
              value={newTransaction.amount}
              onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
              fullWidth
              required
              placeholder="0.00"
            />
            <TextField
              select
              label="Category"
              value={newTransaction.category}
              onChange={(e) => setNewTransaction({ ...newTransaction, category: e.target.value })}
              fullWidth
              required
            >
              {categories.map((category) => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Account"
              value={newTransaction.account_id}
              onChange={(e) => setNewTransaction({ ...newTransaction, account_id: e.target.value })}
              fullWidth
              required
            >
              {accounts.map((account) => (
                <MenuItem key={account.id} value={account.id}>
                  {account.account_name} ({account.account_type})
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Type"
              value={newTransaction.transaction_type}
              onChange={(e) => setNewTransaction({ ...newTransaction, transaction_type: e.target.value as 'debit' | 'credit' })}
              fullWidth
              required
            >
              <MenuItem value="debit">Expense (Debit)</MenuItem>
              <MenuItem value="credit">Income (Credit)</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleAddTransaction}
            disabled={!newTransaction.description || !newTransaction.amount || !newTransaction.category || !newTransaction.account_id}
          >
            Add Transaction
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Transaction Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Transaction</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Description"
              value={newTransaction.description}
              onChange={(e) => setNewTransaction({ ...newTransaction, description: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Amount"
              type="number"
              value={newTransaction.amount}
              onChange={(e) => setNewTransaction({ ...newTransaction, amount: e.target.value })}
              fullWidth
              required
            />
            <TextField
              select
              label="Category"
              value={newTransaction.category}
              onChange={(e) => setNewTransaction({ ...newTransaction, category: e.target.value })}
              fullWidth
              required
            >
              {categories.map((category) => (
                <MenuItem key={category} value={category}>
                  {category}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Type"
              value={newTransaction.transaction_type}
              onChange={(e) => setNewTransaction({ ...newTransaction, transaction_type: e.target.value as 'debit' | 'credit' })}
              fullWidth
              required
            >
              <MenuItem value="debit">Expense (Debit)</MenuItem>
              <MenuItem value="credit">Income (Credit)</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleUpdateTransaction}
            disabled={!newTransaction.description || !newTransaction.amount || !newTransaction.category}
          >
            Update Transaction
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Expenses;
