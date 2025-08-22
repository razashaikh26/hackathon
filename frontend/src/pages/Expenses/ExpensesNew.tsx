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
import { apiService, ExpenseData, Transaction as ApiTransaction, Account } from '../../services/api';

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
  'Other'
];

const Expenses: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
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
    } finally {
      setLoading(false);
    }
  };

  const handleAddTransaction = async () => {
    try {
      const user = getCurrentUser();
      if (!user) {
        throw new Error('User not found');
      }

      if (!newTransaction.account_id) {
        setError('Please select an account');
        return;
      }

      const transactionData = {
        account_id: newTransaction.account_id,
        amount: newTransaction.transaction_type === 'debit' 
          ? -Math.abs(parseFloat(newTransaction.amount))
          : Math.abs(parseFloat(newTransaction.amount)),
        description: newTransaction.description,
        category: newTransaction.category,
        transaction_type: newTransaction.transaction_type,
        currency: user.currency_preference || 'INR'
      };

      await apiService.createTransaction(transactionData);

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

      // Refresh data
      await fetchExpenseData();

    } catch (error) {
      console.error('Error adding transaction:', error);
      setError('Failed to add transaction. Please try again.');
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

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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
        <Button variant="contained" onClick={fetchExpenseData} startIcon={<RefreshIcon />}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Expenses & Transactions
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          disabled={accounts.length === 0}
        >
          Add Transaction
        </Button>
      </Box>

      {accounts.length === 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          No accounts found. Please create an account first to add transactions.
        </Alert>
      )}

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Transactions" />
        <Tab label="Categories" />
        <Tab label="Budget Tracking" />
      </Tabs>

      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Total Monthly Expenses */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingDownIcon color="error" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Monthly Expenses
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold" color="error.main">
                  {formatCurrency(expenseData?.totalMonthly || 0)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Number of Transactions */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <ReceiptIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Transactions
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {transactions.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Categories */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CategoryIcon color="secondary" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Categories
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold">
                  {expenseData?.categories.length || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Anomalies */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <WarningIcon color="warning" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Large Transactions
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  {transactions.filter(t => t.isAnomaly).length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Expense Categories Chart */}
          {expenseData && expenseData.categories.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Expenses by Category
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={expenseData.categories}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="amount"
                      >
                        {expenseData.categories.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Recent Transactions */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Transactions
                </Typography>
                <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {transactions.slice(0, 5).map((transaction) => (
                    <Box key={transaction.id} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 1, borderBottom: '1px solid #eee' }}>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {transaction.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {transaction.date} • {transaction.category}
                        </Typography>
                      </Box>
                      <Box sx={{ textAlign: 'right' }}>
                        <Typography variant="body2" color={transaction.transaction_type === 'debit' ? 'error.main' : 'success.main'} fontWeight="medium">
                          {transaction.transaction_type === 'debit' ? '-' : '+'}{formatCurrency(Math.abs(transaction.amount))}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {transaction.account}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              All Transactions
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Account</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell>{transaction.date}</TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">{transaction.description}</Typography>
                          {transaction.isAnomaly && (
                            <Chip label="Large Amount" size="small" color="warning" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip label={transaction.category} size="small" />
                      </TableCell>
                      <TableCell>{transaction.account}</TableCell>
                      <TableCell align="right">
                        <Typography 
                          color={transaction.transaction_type === 'debit' ? 'error.main' : 'success.main'}
                          fontWeight="medium"
                        >
                          {transaction.transaction_type === 'debit' ? '-' : '+'}{formatCurrency(Math.abs(transaction.amount))}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={transaction.transaction_type} 
                          size="small" 
                          color={transaction.transaction_type === 'debit' ? 'error' : 'success'} 
                        />
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
