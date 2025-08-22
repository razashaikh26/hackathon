import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  Alert,
} from '@mui/material';
import {
  RecordVoiceOver,
  VolumeUp,
  Language,
  Security,
  Speed,
  Psychology,
  Mic,
  Speaker,
  Phone,
  Chat,
} from '@mui/icons-material';
import VoiceAssistant from '../../components/VoiceAssistant/VoiceAssistant';
import { VoiceResponse } from '../../services/vapiVoiceService';

const VoiceInput: React.FC = () => {
  const [recentResponses, setRecentResponses] = useState<VoiceResponse[]>([]);

  const handleVoiceResponse = (response: VoiceResponse) => {
    setRecentResponses(prev => [response, ...prev.slice(0, 4)]); // Keep last 5 responses
  };

  const features = [
    {
      icon: <Psychology color="primary" />,
      title: 'SQL-like Query Intelligence',
      description: 'Advanced financial query processing with database-like precision',
    },
    {
      icon: <Language color="primary" />,
      title: 'Multi-Language Support',
      description: 'Supports English, Hindi, Tamil, Telugu and more regional languages',
    },
    {
      icon: <Security color="primary" />,
      title: 'Secure Processing',
      description: 'Bank-level security with encrypted voice data and secure API calls',
    },
    {
      icon: <Speed color="primary" />,
      title: 'Real-Time Analysis',
      description: 'Instant voice processing with intelligent financial data analysis',
    },
  ];

  const voiceCapabilities = [
    { icon: <Mic />, text: 'Advanced Voice Recording with Noise Cancellation' },
    { icon: <Speaker />, text: 'High-Quality Computer Speaker Audio Output' },
    { icon: <Chat />, text: 'Natural Language Financial Query Processing' },
    { icon: <Phone />, text: 'Phone Call Integration (Coming Soon)' },
  ];

  const sqlLikeQueries = [
    {
      category: 'Balance Queries',
      examples: [
        '"Check my account balance"',
        '"What is my total savings?"',
        '"Show me my current balance"'
      ],
      sqlEquivalent: 'SELECT SUM(amount) FROM accounts WHERE user_id = ?'
    },
    {
      category: 'Expense Analysis',
      examples: [
        '"Show my monthly expenses"',
        '"Where did I spend money?"',
        '"Expense breakdown by category"'
      ],
      sqlEquivalent: 'SELECT category, SUM(amount) FROM expenses GROUP BY category'
    },
    {
      category: 'Portfolio Tracking',
      examples: [
        '"How is my portfolio performing?"',
        '"Show my investment status"',
        '"Stock performance today"'
      ],
      sqlEquivalent: 'SELECT symbol, current_value, profit_loss FROM portfolio'
    },
    {
      category: 'Goal Progress',
      examples: [
        '"How close am I to my goals?"',
        '"Savings goal progress"',
        '"Financial target status"'
      ],
      sqlEquivalent: 'SELECT goal_name, (current/target)*100 as progress FROM goals'
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box mb={4}>
        <Typography variant="h3" component="h1" gutterBottom display="flex" alignItems="center">
          <RecordVoiceOver sx={{ mr: 2, fontSize: 'inherit', color: 'primary.main' }} />
          FinVoice AI Assistant
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Advanced voice-powered financial management with SQL-like query capabilities
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Ask natural language questions and get instant financial insights with intelligent voice responses
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap" mt={2}>
          <Chip label="SQL-like Queries" color="primary" />
          <Chip label="Real-time Processing" color="secondary" />
          <Chip label="Multi-language" color="info" />
          <Chip label="Computer Audio Output" color="success" />
          <Chip label="Financial Intelligence" color="warning" />
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Main Voice Assistant */}
        <Grid item xs={12} lg={8}>
          <VoiceAssistant onResponse={handleVoiceResponse} />
          
          {/* Recent Responses */}
          {recentResponses.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Voice Interactions
                </Typography>
                <List>
                  {recentResponses.map((response, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemIcon>
                          <VolumeUp color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={response.text_response}
                          secondary={`Response ${index + 1} - ${response.success ? 'Success' : 'Failed'}`}
                        />
                      </ListItem>
                      {index < recentResponses.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Features & Capabilities */}
        <Grid item xs={12} lg={4}>
          {/* Features */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Voice Features
              </Typography>
              <List dense>
                {features.map((feature, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {feature.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={feature.title}
                      secondary={feature.description}
                      primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: 500 }}
                      secondaryTypographyProps={{ fontSize: '0.8rem' }}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Voice Capabilities */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Voice Capabilities
              </Typography>
              <List dense>
                {voiceCapabilities.map((capability, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {capability.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={capability.text}
                      primaryTypographyProps={{ fontSize: '0.9rem' }}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Enhanced SQL-like Query Examples */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                SQL-like Voice Queries
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Speak naturally - our AI converts your voice to intelligent financial queries
              </Typography>
              {sqlLikeQueries.map((queryType, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    {queryType.category}
                  </Typography>
                  <List dense>
                    {queryType.examples.map((example, exIndex) => (
                      <ListItem key={exIndex} sx={{ py: 0, pl: 2 }}>
                        <ListItemText 
                          primary={example}
                          primaryTypographyProps={{ fontSize: '0.85rem', fontStyle: 'italic' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                  <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 0.5, borderRadius: 0.5, display: 'block' }}>
                    SQL: {queryType.sqlEquivalent}
                  </Typography>
                  {index < sqlLikeQueries.length - 1 && <Divider sx={{ mt: 1 }} />}
                </Box>
              ))}
            </CardContent>
          </Card>
          {/* Enhanced Instructions */}
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2" fontWeight={500} gutterBottom>
              How to Use SQL-like Voice Queries:
            </Typography>
            <Typography variant="body2" component="div">
              1. Click the microphone to start recording
              <br />
              2. Ask your financial question naturally (e.g., "Check my balance")
              <br />
              3. AI converts your voice to SQL-like queries automatically
              <br />
              4. Listen to comprehensive financial analysis through speakers
              <br />
              5. View query breakdown and SQL equivalents
            </Typography>
          </Alert>

          <Alert severity="success">
            <Typography variant="body2">
              <strong>🎵 Enhanced Audio Output:</strong> Responses include detailed financial analysis, recommendations, and market insights played through your computer speakers automatically.
            </Typography>
          </Alert>

          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>💡 Smart Query Examples:</strong> Try saying "Show my expenses", "Portfolio performance", "Goal progress", or "Check balance" for instant SQL-like financial analysis.
            </Typography>
          </Alert>
        </Grid>
      </Grid>
    </Container>
  );
};

export default VoiceInput;
