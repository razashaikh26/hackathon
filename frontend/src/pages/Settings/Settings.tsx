import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Avatar,
  CircularProgress,
} from '@mui/material';
import {
  Person as PersonIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Palette as ThemeIcon,
  Settings as SettingsIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  VpnKey as VpnKeyIcon,
  Backup as BackupIcon,
  Download as ExportIcon,
  Upload as ImportIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { apiService } from '../../services/api';

interface UserSettings {
  id: string;
  email: string;
  full_name: string;
  risk_tolerance: string;
  currency_preference: string;
  annual_income?: number;
  is_active: boolean;
  created_at: string;
}

interface NotificationSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  weekly_reports: boolean;
  goal_reminders: boolean;
  transaction_alerts: boolean;
  market_updates: boolean;
  ai_insights: boolean;
}

interface PrivacySettings {
  data_sharing: boolean;
  analytics_tracking: boolean;
  marketing_emails: boolean;
  third_party_integrations: boolean;
}

const Settings: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editingProfile, setEditingProfile] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [userSettings, setUserSettings] = useState<UserSettings | null>(null);
  const [notifications, setNotifications] = useState<NotificationSettings>({
    email_notifications: true,
    push_notifications: true,
    weekly_reports: true,
    goal_reminders: true,
    transaction_alerts: true,
    market_updates: false,
    ai_insights: true,
  });
  const [privacy, setPrivacy] = useState<PrivacySettings>({
    data_sharing: false,
    analytics_tracking: true,
    marketing_emails: false,
    third_party_integrations: false,
  });
  const [profileForm, setProfileForm] = useState({
    full_name: '',
    email: '',
    risk_tolerance: '',
    currency_preference: '',
    annual_income: '',
  });

  const riskToleranceOptions = [
    'conservative',
    'moderate',
    'aggressive'
  ];

  const currencyOptions = [
    'INR',
    'EUR',
    'GBP',
    'JPY',
    'CAD',
    'AUD'
  ];

  useEffect(() => {
    fetchUserSettings();
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

  const fetchUserSettings = async () => {
    try {
      setLoading(true);
      setError(null);

      const user = getCurrentUser();
      if (!user) {
        throw new Error('No user found. Please login again.');
      }

      // Fetch user data from API
      const userData = await apiService.getUser(user.id);
      setUserSettings(userData);
      
      // Populate form with current data
      setProfileForm({
        full_name: userData.full_name || '',
        email: userData.email || '',
        risk_tolerance: userData.risk_tolerance || 'moderate',
        currency_preference: userData.currency_preference || 'INR',
        annual_income: (userData as any).annual_income?.toString() || '',
      });

    } catch (error) {
      console.error('Error fetching user settings:', error);
      setError('Failed to load user settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      setError(null);

      const user = getCurrentUser();
      if (!user) {
        throw new Error('No user found');
      }

      const updateData = {
        full_name: profileForm.full_name.trim(),
        risk_tolerance: profileForm.risk_tolerance,
        currency_preference: profileForm.currency_preference,
        annual_income: profileForm.annual_income ? parseInt(profileForm.annual_income) : null,
      };

      const updatedUser = await apiService.updateUser(user.id, updateData);
      
      // Update localStorage
      localStorage.setItem('currentUser', JSON.stringify(updatedUser));
      
      setUserSettings(updatedUser);
      setEditingProfile(false);
      setSuccess('Profile updated successfully!');
      setTimeout(() => setSuccess(null), 3000);

    } catch (error) {
      console.error('Error updating profile:', error);
      setError('Failed to update profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleNotificationChange = (key: keyof NotificationSettings) => {
    setNotifications(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handlePrivacyChange = (key: keyof PrivacySettings) => {
    setPrivacy(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleExportData = async () => {
    try {
      const user = getCurrentUser();
      if (!user) return;

      // Create export data
      const exportData = {
        profile: userSettings,
        settings: {
          notifications,
          privacy,
        },
        exported_at: new Date().toISOString(),
        version: '1.0'
      };

      // Download as JSON file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `finvoice_settings_${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);

      setSuccess('Settings exported successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      setError('Failed to export settings.');
    }
  };

  const handleDeleteAccount = async () => {
    // This would typically call an API to delete the account
    setError('Account deletion is not implemented yet. Contact support for assistance.');
    setShowDeleteDialog(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <SettingsIcon sx={{ mr: 2, fontSize: 32 }} color="primary" />
        <Typography variant="h4" fontWeight="bold">
          Settings
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab icon={<PersonIcon />} label="Profile" />
        <Tab icon={<NotificationsIcon />} label="Notifications" />
        <Tab icon={<SecurityIcon />} label="Privacy & Security" />
        <Tab icon={<ThemeIcon />} label="Preferences" />
        <Tab icon={<BackupIcon />} label="Data & Backup" />
      </Tabs>

      {/* Profile Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Avatar sx={{ width: 80, height: 80, mx: 'auto', mb: 2, bgcolor: 'primary.main' }}>
                  {userSettings?.full_name?.charAt(0) || userSettings?.email?.charAt(0) || 'U'}
                </Avatar>
                <Typography variant="h6">{userSettings?.full_name || 'User'}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {userSettings?.email}
                </Typography>
                <Chip 
                  label={userSettings?.is_active ? 'Active' : 'Inactive'} 
                  color={userSettings?.is_active ? 'success' : 'error'}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6">Profile Information</Typography>
                  {!editingProfile ? (
                    <IconButton onClick={() => setEditingProfile(true)}>
                      <EditIcon />
                    </IconButton>
                  ) : (
                    <Box>
                      <IconButton onClick={handleSaveProfile} disabled={saving} color="primary">
                        <SaveIcon />
                      </IconButton>
                      <IconButton onClick={() => setEditingProfile(false)} disabled={saving}>
                        <CancelIcon />
                      </IconButton>
                    </Box>
                  )}
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Full Name"
                      value={profileForm.full_name}
                      onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                      disabled={!editingProfile}
                      variant={editingProfile ? 'outlined' : 'filled'}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      value={profileForm.email}
                      disabled
                      variant="filled"
                      helperText="Email cannot be changed"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      select
                      label="Risk Tolerance"
                      value={profileForm.risk_tolerance}
                      onChange={(e) => setProfileForm({ ...profileForm, risk_tolerance: e.target.value })}
                      disabled={!editingProfile}
                      variant={editingProfile ? 'outlined' : 'filled'}
                    >
                      {riskToleranceOptions.map((option) => (
                        <MenuItem key={option} value={option}>
                          {option.charAt(0).toUpperCase() + option.slice(1)}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      select
                      label="Preferred Currency"
                      value={profileForm.currency_preference}
                      onChange={(e) => setProfileForm({ ...profileForm, currency_preference: e.target.value })}
                      disabled={!editingProfile}
                      variant={editingProfile ? 'outlined' : 'filled'}
                    >
                      {currencyOptions.map((option) => (
                        <MenuItem key={option} value={option}>
                          {option}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Annual Income (Optional)"
                      type="number"
                      value={profileForm.annual_income}
                      onChange={(e) => setProfileForm({ ...profileForm, annual_income: e.target.value })}
                      disabled={!editingProfile}
                      variant={editingProfile ? 'outlined' : 'filled'}
                      helperText="Used for better financial recommendations"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Notifications Tab */}
      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Notification Preferences
            </Typography>
            <List>
              {Object.entries(notifications).map(([key, value]) => (
                <ListItem key={key}>
                  <ListItemText
                    primary={key.split('_').map(word => 
                      word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ')}
                    secondary={getNotificationDescription(key)}
                  />
                  <ListItemSecondaryAction>
                    <Switch
                      checked={value}
                      onChange={() => handleNotificationChange(key as keyof NotificationSettings)}
                    />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Privacy & Security Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Privacy Settings
                </Typography>
                <List>
                  {Object.entries(privacy).map(([key, value]) => (
                    <ListItem key={key}>
                      <ListItemText
                        primary={key.split('_').map(word => 
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')}
                        secondary={getPrivacyDescription(key)}
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          checked={value}
                          onChange={() => handlePrivacyChange(key as keyof PrivacySettings)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security Options
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<VpnKeyIcon />}
                    fullWidth
                    disabled
                  >
                    Change Password
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<SecurityIcon />}
                    fullWidth
                    disabled
                  >
                    Two-Factor Authentication
                  </Button>
                  <Alert severity="info" icon={<InfoIcon />}>
                    Security features are coming soon. Your data is encrypted and secure.
                  </Alert>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Preferences Tab */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Display Preferences
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Alert severity="info">
                    Theme customization and advanced display options are coming in a future update.
                  </Alert>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Dark Mode"
                    disabled
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Compact View"
                    disabled
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Advanced Charts"
                    disabled
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Regional Settings
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      select
                      label="Date Format"
                      value="MM/DD/YYYY"
                      disabled
                    >
                      <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                      <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                      <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                    </TextField>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      select
                      label="Time Zone"
                      value="UTC"
                      disabled
                    >
                      <MenuItem value="UTC">UTC</MenuItem>
                      <MenuItem value="EST">Eastern Time</MenuItem>
                      <MenuItem value="PST">Pacific Time</MenuItem>
                    </TextField>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Data & Backup Tab */}
      {tabValue === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Data Management
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<ExportIcon />}
                    onClick={handleExportData}
                    fullWidth
                  >
                    Export All Data
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<ImportIcon />}
                    fullWidth
                    disabled
                  >
                    Import Data
                  </Button>
                  <Alert severity="info">
                    Export includes your profile, settings, and preferences. Financial data export coming soon.
                  </Alert>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="error">
                  Danger Zone
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={() => setShowDeleteDialog(true)}
                    fullWidth
                  >
                    Delete Account
                  </Button>
                  <Alert severity="warning">
                    Deleting your account will permanently remove all your data. This action cannot be undone.
                  </Alert>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Delete Account Dialog */}
      <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)}>
        <DialogTitle color="error">Delete Account</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete your account? This will permanently remove all your data and cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDeleteDialog(false)}>Cancel</Button>
          <Button onClick={handleDeleteAccount} color="error" variant="contained">
            Delete Account
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Helper functions for descriptions
const getNotificationDescription = (key: string): string => {
  const descriptions: Record<string, string> = {
    email_notifications: 'Receive important updates via email',
    push_notifications: 'Get real-time notifications in your browser',
    weekly_reports: 'Weekly summary of your financial activity',
    goal_reminders: 'Reminders about your financial goals progress',
    transaction_alerts: 'Notifications for new transactions',
    market_updates: 'Updates about market conditions and trends',
    ai_insights: 'Personalized AI-powered financial insights',
  };
  return descriptions[key] || '';
};

const getPrivacyDescription = (key: string): string => {
  const descriptions: Record<string, string> = {
    data_sharing: 'Share anonymized data for product improvement',
    analytics_tracking: 'Allow usage analytics to improve user experience',
    marketing_emails: 'Receive promotional emails and product updates',
    third_party_integrations: 'Allow connections with external financial services',
  };
  return descriptions[key] || '';
};

export default Settings;
