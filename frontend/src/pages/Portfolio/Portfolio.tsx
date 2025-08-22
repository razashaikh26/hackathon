import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  TextField,
  DialogActions,
  MenuItem,
  Alert,
  Tabs,
  Tab,
  CircularProgress,
  Tooltip as MuiTooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Add,
  Edit,
  Delete,
  Assessment,
  AccountBalance,
  ShowChart,
  Refresh,
} from '@mui/icons-material';
import { 
  PieChart, 
  Pie, 
  Cell, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Area,
  AreaChart
} from 'recharts';

// API Service
import { apiService, Portfolio as PortfolioData } from '../../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const Portfolio: React.FC = () => {
  const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null);
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingHolding, setEditingHolding] = useState<any>(null);
  const [tabValue, setTabValue] = useState(0);
  const [newAsset, setNewAsset] = useState({
    symbol: '',
    name: '',
    type: 'stock' as 'stock' | 'crypto' | 'bond' | 'mutual_fund',
    quantity: '',
    purchasePrice: ''
  });

  useEffect(() => {
    fetchPortfolioData();
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

  const fetchPortfolioData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Get current user from localStorage
      const savedUser = localStorage.getItem('currentUser');
      if (!savedUser) {
        throw new Error('No user found. Please login again.');
      }
      
      const currentUser = JSON.parse(savedUser);
      console.log('Fetching portfolio data for user:', currentUser.id);
      
      // Fetch real data from database API
      const [holdingsData, overviewData] = await Promise.all([
        apiService.getUserHoldings(currentUser.id),
        apiService.getFinancialOverview(currentUser.id)
      ]);
      
      console.log('Holdings data:', holdingsData);
      console.log('Overview data:', overviewData);
      
      // Transform holdings data to match interface
      const transformedHoldings = holdingsData.map((holding: any) => ({
        id: holding.id,
        user_id: currentUser.id,
        symbol: holding.symbol,
        name: holding.name,
        asset_type: holding.asset_type,
        quantity: Number(holding.quantity),
        average_price: Number(holding.average_price),
        current_price: Number(holding.current_price),
        market_value: Number(holding.current_value || holding.market_value),
        total_gain_loss: Number(holding.unrealized_pnl || 0),
        total_gain_loss_percentage: Number(holding.unrealized_pnl_percent || 0),
        currency: holding.currency || 'INR',
        is_active: holding.is_active,
        purchase_date: holding.purchase_date || new Date().toISOString(),
        created_at: holding.created_at || new Date().toISOString()
      }));
      
      // Transform portfolio data
      const portfolioValue = overviewData.portfolio?.total_value || 0;
      const totalPnL = overviewData.portfolio?.total_gain_loss || 0;
      const totalPnLPercent = overviewData.portfolio?.total_gain_loss_percentage || 0;
      
      const transformedData: PortfolioData = {
        totalValue: portfolioValue,
        todayChange: 0, // Would need historical data
        todayChangePercent: 0,
        totalGainLoss: totalPnL,
        gainLossPercentage: totalPnLPercent,
        currency: 'INR',
        holdings: transformedHoldings
      };

      setPortfolioData(transformedData);
      setError(null); // Clear any previous errors since we got data successfully
      
      try {
        const perfData = await apiService.getPortfolioPerformance(currentUser.id);
        setPerformanceData(perfData);
      } catch (e) {
        console.log('Performance data not available:', e);
      }

    } catch (error) {
      console.error('Error fetching portfolio data:', error);
      setError('Unable to load portfolio data from database. Please check your connection.');
      
      // Fallback demo data with Indian context
      const demoHoldings = [
        {
          id: '1',
          user_id: 'demo',
          symbol: 'RELIANCE',
          name: 'Reliance Industries Ltd',
          asset_type: 'stock',
          quantity: 50,
          average_price: 2450,
          current_price: 2500,
          market_value: 125000,
          total_gain_loss: 2500,
          total_gain_loss_percentage: 2.04,
          currency: 'INR',
          is_active: true,
          purchase_date: '2024-01-15',
          created_at: '2024-01-15'
        },
        {
          id: '2',
          user_id: 'demo',
          symbol: 'TCS',
          name: 'Tata Consultancy Services',
          asset_type: 'stock',
          quantity: 30,
          average_price: 3600,
          current_price: 3720,
          market_value: 111600,
          total_gain_loss: 3600,
          total_gain_loss_percentage: 3.33,
          currency: 'INR',
          is_active: true,
          purchase_date: '2024-02-10',
          created_at: '2024-02-10'
        }
      ];
      
      setPortfolioData({
        totalValue: 850000, // ₹8.5 lakhs
        todayChange: 12000, // ₹12k gain today
        todayChangePercent: 1.4, // 1.4% gain today
        totalGainLoss: 125000, // ₹1.25 lakhs gain
        gainLossPercentage: 17.2,
        currency: 'INR',
        holdings: demoHoldings
      });
    } finally {
      setLoading(false);
    }
  };

  // Add holding functionality

  const formatCurrency = (amount: number, currency: string = 'INR') => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const getAssetTypeColor = (type: string) => {
    const colors: { [key: string]: 'primary' | 'secondary' | 'success' | 'warning' | 'info' | 'error' } = {
      stock: 'primary',
      bond: 'secondary',
      etf: 'success',
      crypto: 'warning',
      mutual_fund: 'info',
    };
    return colors[type] || 'primary';
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAddAsset = async () => {
    try {
      const user = getCurrentUser();
      if (!user) {
        throw new Error('User not found');
      }

      const holdingData = {
        symbol: newAsset.symbol.toUpperCase(),
        name: newAsset.name,
        asset_type: newAsset.type,
        quantity: parseInt(newAsset.quantity),
        average_price: parseFloat(newAsset.purchasePrice),
        currency: 'INR'
      };

      await apiService.createHolding(user.id, holdingData);
      
      setOpenDialog(false);
      setNewAsset({
        symbol: '',
        name: '',
        type: 'stock',
        quantity: '',
        purchasePrice: ''
      });
      
      // Refresh portfolio data
      await fetchPortfolioData();
      
    } catch (error) {
      console.error('Error adding asset:', error);
      setError('Failed to add asset. Please try again.');
    }
  };

  const handleEditAsset = (holding: any) => {
    setEditingHolding(holding);
    setNewAsset({
      symbol: holding.symbol,
      name: holding.name,
      type: holding.asset_type || 'stock',
      quantity: holding.quantity.toString(),
      purchasePrice: holding.average_price.toString()
    });
    setOpenEditDialog(true);
  };

  const handleUpdateAsset = async () => {
    try {
      const user = getCurrentUser();
      if (!user || !editingHolding) {
        throw new Error('User or holding not found');
      }

      const holdingData = {
        symbol: newAsset.symbol.toUpperCase(),
        name: newAsset.name,
        asset_type: newAsset.type,
        quantity: parseInt(newAsset.quantity),
        average_price: parseFloat(newAsset.purchasePrice),
        currency: 'INR'
      };

      await apiService.updateHolding(editingHolding.id, holdingData);
      
      setOpenEditDialog(false);
      setEditingHolding(null);
      setNewAsset({
        symbol: '',
        name: '',
        type: 'stock',
        quantity: '',
        purchasePrice: ''
      });
      
      // Refresh portfolio data
      await fetchPortfolioData();
      
    } catch (error) {
      console.error('Error updating asset:', error);
      setError('Failed to update asset. Please try again.');
    }
  };

  const handleDeleteAsset = async (holdingId: string) => {
    if (!window.confirm('Are you sure you want to delete this holding?')) {
      return;
    }

    try {
      const user = getCurrentUser();
      if (!user) {
        throw new Error('User not found');
      }

      await apiService.deleteHolding(holdingId);
      
      // Refresh portfolio data
      await fetchPortfolioData();
      
    } catch (error) {
      console.error('Error deleting asset:', error);
      setError('Failed to delete asset. Please try again.');
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Portfolio
        </Typography>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
          <Typography variant="h6" sx={{ ml: 2 }}>
            Loading portfolio data...
          </Typography>
        </Box>
      </Box>
    );
  }

  if (error && !portfolioData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" action={
          <IconButton onClick={fetchPortfolioData} size="small">
            <Refresh />
          </IconButton>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!portfolioData) {
    return (
      <Alert severity="warning">
        No portfolio data available. Please try refreshing.
      </Alert>
    );
  }

  // Calculate allocation based on holdings
  const allocation = portfolioData.holdings.reduce((acc, holding) => {
    const existing = acc.find(item => item.name === holding.asset_type.toUpperCase());
    if (existing) {
      existing.value += holding.market_value;
    } else {
      acc.push({ name: holding.asset_type.toUpperCase(), value: holding.market_value });
    }
    return acc;
  }, [] as { name: string; value: number }[]);

  // Convert to percentage
  const allocationPercentage = allocation.map(item => ({
    name: item.name,
    value: (item.value / portfolioData.totalValue) * 100
  }));

  // Performance history (mock data for now)
  const performanceHistory = [
    { date: 'Jan', value: 720000 },
    { date: 'Feb', value: 750000 },
    { date: 'Mar', value: 780000 },
    { date: 'Apr', value: 800000 },
    { date: 'May', value: 825000 },
    { date: 'Jun', value: 850000 },
    { date: 'Jul', value: 870000 },
    { date: 'Aug', value: portfolioData.totalValue }
  ];

  const riskMetrics = [
    { name: 'Conservative', value: 25, color: '#00C49F' },
    { name: 'Moderate', value: 55, color: '#FFBB28' },
    { name: 'Aggressive', value: 20, color: '#FF8042' }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Portfolio
          <Chip 
            label="INR" 
            color="primary" 
            size="small" 
            sx={{ ml: 2 }}
          />
        </Typography>
        <Box display="flex" gap={1}>
          <MuiTooltip title="Refresh data">
            <IconButton onClick={fetchPortfolioData} size="small">
              <Refresh />
            </IconButton>
          </MuiTooltip>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenDialog(true)}
          >
            Add Asset
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error} - Showing demo data below.
        </Alert>
      )}

      {portfolioData.totalGainLoss > 0 ? (
        <Alert severity="success" sx={{ mb: 3 }}>
          Your portfolio is up {formatPercentage(portfolioData.gainLossPercentage)} this period!
        </Alert>
      ) : (
        <Alert severity="info" sx={{ mb: 3 }}>
          Market volatility detected. Consider reviewing your allocation strategy.
        </Alert>
      )}

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" icon={<Assessment />} />
        <Tab label="Holdings" icon={<AccountBalance />} />
        <Tab label="Performance" icon={<ShowChart />} />
      </Tabs>

      {tabValue === 0 && (
        <>
          {/* Portfolio Summary */}
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <AccountBalance color="primary" sx={{ mr: 1 }} />
                    <Typography color="text.secondary">
                      Total Value
                    </Typography>
                  </Box>
                  <Typography variant="h4" component="div">
                    {formatCurrency(portfolioData.totalValue, portfolioData.currency)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {portfolioData.totalGainLoss > 0 ? (
                      <TrendingUp color="success" sx={{ mr: 1 }} />
                    ) : (
                      <TrendingDown color="error" sx={{ mr: 1 }} />
                    )}
                    <Typography color="text.secondary">
                      Total Gain/Loss
                    </Typography>
                  </Box>
                  <Typography
                    variant="h4"
                    component="div"
                    color={portfolioData.totalGainLoss > 0 ? 'success.main' : 'error.main'}
                  >
                    {formatCurrency(portfolioData.totalGainLoss, portfolioData.currency)}
                  </Typography>
                  <Typography
                    variant="body1"
                    color={portfolioData.totalGainLoss > 0 ? 'success.main' : 'error.main'}
                  >
                    {formatPercentage(portfolioData.gainLossPercentage)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Assessment color="primary" sx={{ mr: 1 }} />
                    <Typography color="text.secondary">
                      Asset Count
                    </Typography>
                  </Box>
                  <Typography variant="h4" component="div">
                    {portfolioData.holdings.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Diversified holdings
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Charts */}
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Asset Allocation
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={allocationPercentage}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name} ${value.toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {allocationPercentage.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`${Number(value).toFixed(1)}%`, 'Allocation']} />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Performance History
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={performanceHistory}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis tickFormatter={(value) => `₹${(value/100000).toFixed(1)}L`} />
                      <Tooltip formatter={(value) => [formatCurrency(value as number), 'Portfolio Value']} />
                      <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Risk Distribution */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={riskMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value}%`, 'Allocation']} />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </>
      )}

      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Holdings
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Symbol</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Current Price</TableCell>
                    <TableCell align="right">Total Value</TableCell>
                    <TableCell align="right">Gain/Loss</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {portfolioData.holdings.map((holding) => (
                    <TableRow key={holding.id}>
                      <TableCell component="th" scope="row">
                        <Typography variant="body2" fontWeight="bold">
                          {holding.symbol}
                        </Typography>
                      </TableCell>
                      <TableCell>{holding.name}</TableCell>
                      <TableCell>
                        <Chip
                          label={holding.asset_type.toUpperCase()}
                          color={getAssetTypeColor(holding.asset_type)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">{holding.quantity}</TableCell>
                      <TableCell align="right">
                        {formatCurrency(holding.current_price, holding.currency)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(holding.market_value, holding.currency)}
                      </TableCell>
                      <TableCell align="right">
                        <Box
                          color={holding.total_gain_loss > 0 ? 'success.main' : 'error.main'}
                        >
                          {formatCurrency(holding.total_gain_loss, holding.currency)} (
                          {formatPercentage(holding.total_gain_loss_percentage)})
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small" onClick={() => handleEditAsset(holding)}>
                          <Edit />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDeleteAsset(holding.id)}>
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {portfolioData.holdings.length === 0 && (
              <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
                No holdings found. Add your first investment to get started!
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Portfolio Performance Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={performanceHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis tickFormatter={(value) => `₹${(value/100000).toFixed(1)}L`} />
                    <Tooltip formatter={(value) => [formatCurrency(value as number), 'Portfolio Value']} />
                    <Legend />
                    <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Asset Performance
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={portfolioData.holdings.map(holding => ({ 
                    symbol: holding.symbol, // Keep original symbol
                    performance: holding.total_gain_loss_percentage 
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="symbol" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value}%`, 'Performance']} />
                    <Bar dataKey="performance" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Value Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={portfolioData.holdings.map(holding => ({ 
                        name: holding.symbol, // Keep original symbol
                        value: holding.market_value 
                      }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {portfolioData.holdings.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [formatCurrency(value as number), 'Value']} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Add Asset Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Asset</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Symbol"
                placeholder="e.g., RELIANCE, TCS, HDFCBANK"
                value={newAsset.symbol}
                onChange={(e) => setNewAsset({ ...newAsset, symbol: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                placeholder="e.g., Reliance Industries Limited"
                value={newAsset.name}
                onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Type"
                select
                value={newAsset.type}
                onChange={(e) => setNewAsset({ ...newAsset, type: e.target.value as any })}
              >
                <MenuItem value="stock">Stock</MenuItem>
                <MenuItem value="etf">ETF</MenuItem>
                <MenuItem value="bond">Bond</MenuItem>
                <MenuItem value="crypto">Cryptocurrency</MenuItem>
                <MenuItem value="mutual_fund">Mutual Fund</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Quantity"
                type="number"
                placeholder="0"
                value={newAsset.quantity}
                onChange={(e) => setNewAsset({ ...newAsset, quantity: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Purchase Price (₹)"
                type="number"
                placeholder="0.00"
                value={newAsset.purchasePrice}
                onChange={(e) => setNewAsset({ ...newAsset, purchasePrice: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleAddAsset}
            disabled={!newAsset.symbol || !newAsset.quantity || !newAsset.purchasePrice}
          >
            Add Asset
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Asset Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Asset</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Symbol"
              value={newAsset.symbol}
              onChange={(e) => setNewAsset({ ...newAsset, symbol: e.target.value })}
              fullWidth
            />
            <TextField
              label="Name"
              value={newAsset.name}
              onChange={(e) => setNewAsset({ ...newAsset, name: e.target.value })}
              fullWidth
            />
            <TextField
              select
              label="Type"
              value={newAsset.type}
              onChange={(e) => setNewAsset({ ...newAsset, type: e.target.value as 'stock' | 'crypto' | 'bond' | 'mutual_fund' })}
              fullWidth
            >
              <MenuItem value="stock">Stock</MenuItem>
              <MenuItem value="crypto">Crypto</MenuItem>
              <MenuItem value="bond">Bond</MenuItem>
              <MenuItem value="mutual_fund">Mutual Fund</MenuItem>
            </TextField>
            <TextField
              label="Quantity"
              type="number"
              value={newAsset.quantity}
              onChange={(e) => setNewAsset({ ...newAsset, quantity: e.target.value })}
              fullWidth
            />
            <TextField
              label="Purchase Price"
              type="number"
              value={newAsset.purchasePrice}
              onChange={(e) => setNewAsset({ ...newAsset, purchasePrice: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleUpdateAsset}
            disabled={!newAsset.symbol || !newAsset.quantity || !newAsset.purchasePrice}
          >
            Update Asset
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Portfolio;
