import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  Avatar,
  IconButton,
  Fab,
  Collapse,
  Chip,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Send as SendIcon,
  Close as CloseIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Mic as MicIcon,
  TrendingUp,
  Savings,
  AccountBalance,
} from '@mui/icons-material';
import { apiService } from '../../services/api';

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'suggestion' | 'chart' | 'action';
  data?: any;
}

interface AIResponse {
  advice?: string;
  message?: string;
  type?: string;
  data?: any;
  confidence?: number;
  source?: string;
}

interface ChatBotProps {
  userId?: string;
}

const ChatBot: React.FC<ChatBotProps> = ({ userId = 'demo_user' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: `🤖 Hello! I'm your AI financial advisor powered by advanced analytics and real-time market data.

💡 I can help you with:
📊 Investment planning & portfolio optimization
🎯 Goal-based financial planning (house, education, retirement)
💰 Tax optimization strategies (80C, NPS, ELSS)
📈 Market insights & fund recommendations
💳 Expense analysis & budget optimization
🏦 Insurance & emergency fund planning

I'm trained on Indian financial markets and provide personalized advice based on your income, age, and goals. Try asking me anything like:
• "How should I invest ₹10,000 monthly?"
• "Help me plan for my child's education"
• "How can I save tax this year?"

What would you like to explore today? 🚀`,
      sender: 'bot',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

    const quickActions = [
    { text: 'Analyze Portfolio', icon: <TrendingUp />, action: 'portfolio_analysis' },
    { text: 'Plan Goals', icon: <Savings />, action: 'set_goal' },
    { text: 'Investment Options', icon: <AccountBalance />, action: 'investment_options' },
    { text: 'Expense Analysis', icon: <PersonIcon />, action: 'expense_analysis' },
    { text: 'Tax Planning', icon: <AccountBalance />, action: 'tax_planning' },
    { text: 'Emergency Fund', icon: <Savings />, action: 'emergency_fund' },
    { text: 'Retirement Plan', icon: <TrendingUp />, action: 'retirement_planning' },
    { text: 'Market Insights', icon: <TrendingUp />, action: 'market_insights' }
  ];

  const handleSendMessage = async (text: string, actionType?: string) => {
    if (!text.trim() && !actionType) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: text || `Quick action: ${actionType}`,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      let response: AIResponse;
      
      if (actionType) {
        response = await handleQuickAction(actionType);
      } else {
        // Send to AI advisory endpoint
        const apiResponse = await apiService.getAIAdvice({
          advisory_type: 'general',
          user_profile: {
            user_id: userId,
            query: text
          },
          financial_data: {}
        });
        response = apiResponse as AIResponse;
      }

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: response?.advice || response?.message || 'I\'m here to help with your financial questions!',
        sender: 'bot',
        timestamp: new Date(),
        type: (response?.type as 'text' | 'suggestion' | 'chart' | 'action') || 'text',
        data: response?.data
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Error getting AI response:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again or contact support.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = async (actionType: string): Promise<AIResponse> => {
    switch (actionType) {
      case 'portfolio_analysis':
        const portfolioData = await apiService.getPortfolio();
        return {
          advice: `📊 **Portfolio Analysis:**\n\nYour portfolio is worth ₹${portfolioData.totalValue?.toLocaleString('en-IN')} with ${portfolioData.todayChangePercent > 0 ? 'gains' : 'losses'} of ${Math.abs(portfolioData.todayChangePercent)}% today.\n\n🎯 **Holdings**: ${portfolioData.holdings?.length} investments\n📈 **Performance**: ${portfolioData.todayChangePercent > 0 ? 'Positive momentum' : 'Temporary dip - stay invested'}\n\nWould you like specific rebalancing recommendations or fund suggestions?`,
          type: 'suggestion'
        };
      
      case 'investment_strategy':
        return {
          advice: `🚀 **Investment Strategy Recommendations:**\n\nBased on current market conditions:\n\n📊 **Allocation Strategy:**\n• 60% Large Cap Funds (stability)\n• 25% Mid Cap Funds (growth)\n• 15% International/Debt (diversification)\n\n🎯 **Top Picks:**\n• HDFC Top 100 Fund\n• Mirae Asset Large Cap\n• SBI Small Cap Fund\n\n💡 **Strategy**: Start SIP, increase 10% annually, review quarterly. What's your monthly investment budget?`,
          type: 'suggestion'
        };
      
      case 'tax_planning':
        return {
          advice: `💰 **Tax Optimization Strategy:**\n\n🎯 **Section 80C (₹1.5L limit):**\n• ELSS Funds: ₹8,000/month (growth + tax saving)\n• PPF: ₹4,500/month (long-term wealth)\n\n📊 **Additional Benefits:**\n• NPS: ₹4,000/month (extra ₹50K deduction)\n• Health Insurance: ₹25K deduction\n\n💡 **Potential Savings**: ₹45,000-60,000 annually\n\nPlan by December for current financial year. Need specific fund recommendations?`,
          type: 'suggestion'
        };
      
      case 'goal_planning':
        return {
          advice: `🎯 **Smart Goal Planning:**\n\n� **Popular Financial Goals:**\n🏠 Home Purchase (20% down payment + EMI planning)\n👶 Child Education (₹20-30L corpus needed)\n🌴 Retirement (25x annual income rule)\n🚗 Car Purchase (avoid loans if possible)\n\n📊 **Planning Framework:**\n• Set specific target amounts\n• Define realistic timelines\n• Choose appropriate investments\n• Monitor progress quarterly\n\nWhat specific goal would you like to plan for?`,
          type: 'suggestion'
        };

      case 'market_insights':
        return {
          advice: `📈 **Current Market Insights:**\n\n🎯 **Market Trend**: Bullish momentum in large caps\n📊 **Hot Sectors**: Technology, Healthcare, Financial Services\n💡 **Interest Rates**: Stable at current levels\n\n🚀 **Opportunities:**\n• SIP in quality large cap funds\n• Gradual allocation to mid caps\n• Consider international exposure\n\n⚠️ **Caution**: Avoid timing the market, focus on long-term wealth building\n\nWant sector-specific recommendations?`,
          type: 'suggestion'
        };

      case 'budget_optimization':
        return {
          advice: `💳 **Budget Optimization Strategy:**\n\n📊 **50-30-20 Rule:**\n• 50% Needs (rent, food, utilities)\n• 30% Wants (entertainment, dining)\n• 20% Savings & Investments\n\n💡 **Quick Wins:**\n• Track expenses for 30 days\n• Cancel unused subscriptions\n• Use cashback credit cards\n• Cook at home more often\n\n🎯 **Goal**: Increase savings rate by 5% quarterly\n\nShall I help analyze your current spending pattern?`,
          type: 'suggestion'
        };

      case 'expense_analysis':
        try {
          const expenseData = await apiService.getExpenses();
          const topCategory = expenseData.categories?.[0];
          return {
            advice: `💳 **Your Expense Analysis:**\n\n💰 **Monthly Total**: ₹${expenseData.totalMonthly?.toLocaleString('en-IN')}\n🎯 **Top Category**: ${topCategory?.name} - ₹${topCategory?.amount?.toLocaleString('en-IN')} (${topCategory?.percentage}%)\n\n📊 **Insights:**\n• Budget allocation looks ${topCategory?.percentage > 40 ? 'concentrated - consider diversifying' : 'balanced'}\n• ${topCategory?.percentage > 30 ? 'High spending in ' + topCategory?.name + ' - optimization opportunity' : 'Good spending distribution'}\n\n💡 Would you like specific tips to optimize your ${topCategory?.name} expenses?`,
            type: 'suggestion'
          };
        } catch (error) {
          return {
            advice: '💳 **Expense Analysis:**\n\nTo provide detailed expense analysis, I need access to your transaction data. Here are general optimization tips:\n\n📊 Track expenses for 30 days\n💡 Identify top 3 spending categories\n🎯 Set category-wise budgets\n\nWould you like help setting up expense tracking?',
            type: 'suggestion'
          };
        }

      case 'emergency_fund':
        return {
          advice: `🛡️ **Emergency Fund Strategy:**\n\n🎯 **Target**: 6-12 months of expenses\n💰 **Allocation Strategy:**\n• 50% High-yield savings account (instant access)\n• 30% Liquid mutual funds (1-day withdrawal)\n• 20% Fixed deposits (slightly higher returns)\n\n📊 **Building Plan:**\n• Start with ₹5,000/month\n• Automate transfers on salary day\n• Increase by 10% annually\n\n💡 **Goal**: ₹3-6 lakhs for most Indian families\n\nHow much do you currently have saved for emergencies?`,
          type: 'suggestion'
        };

      case 'retirement_planning':
        return {
          advice: `🌴 **Retirement Planning Guide:**\n\n🎯 **Golden Rules:**\n• Target: 25x annual income as corpus\n• Start early: 20s vs 30s makes huge difference\n• Employer PF: Ensure maximum contribution\n\n📊 **Investment Mix by Age:**\n• 20s-30s: 70% equity, 30% debt\n• 40s: 60% equity, 40% debt\n• 50s+: 50% equity, 50% debt\n\n💰 **Key Instruments:**\n• EPF + VPF (guaranteed returns)\n• NPS (tax benefits + market returns)\n• ELSS mutual funds\n• PPF for long-term wealth\n\nWhat's your current age and monthly income?`,
          type: 'suggestion'
        };
      
      default:
        return {
          advice: 'I can help with comprehensive financial planning! Try asking about investments, tax planning, goal setting, or budget optimization. What interests you most?',
          type: 'text'
        };
    }
  };

  const startVoiceRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-IN';

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
      };

      recognition.onerror = () => {
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } else {
      alert('Speech recognition not supported in this browser');
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-IN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <>
      {/* Floating Chat Button */}
      <Fab
        color="primary"
        aria-label="chat"
        sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
          zIndex: 1000,
        }}
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <CloseIcon /> : <ChatIcon />}
      </Fab>

      {/* Chat Window */}
      <Collapse in={isOpen}>
        <Paper
          elevation={8}
          sx={{
            position: 'fixed',
            bottom: 100,
            right: 20,
            width: 400,
            height: 600,
            zIndex: 1000,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: 2,
              bgcolor: 'primary.main',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <BotIcon />
              <Typography variant="h6">AI Financial Advisor</Typography>
            </Box>
            <IconButton
              size="small"
              onClick={() => setIsOpen(false)}
              sx={{ color: 'white' }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Quick Actions */}
          <Box sx={{ p: 1, bgcolor: 'grey.50' }}>
            <Typography variant="caption" color="textSecondary" sx={{ mb: 1, display: 'block' }}>
              Quick Actions:
            </Typography>
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {quickActions.map((action, index) => (
                <Chip
                  key={index}
                  icon={action.icon}
                  label={action.text}
                  size="small"
                  onClick={() => handleSendMessage('', action.action)}
                  sx={{ fontSize: '0.7rem' }}
                />
              ))}
            </Box>
          </Box>

          <Divider />

          {/* Messages */}
          <Box
            sx={{
              flex: 1,
              overflow: 'auto',
              p: 1,
            }}
          >
            <List dense>
              {messages.map((message) => (
                <ListItem
                  key={message.id}
                  sx={{
                    flexDirection: 'column',
                    alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    py: 0.5,
                  }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 1,
                      maxWidth: '85%',
                      flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 32,
                        height: 32,
                        bgcolor: message.sender === 'user' ? 'primary.main' : 'secondary.main',
                      }}
                    >
                      {message.sender === 'user' ? <PersonIcon /> : <BotIcon />}
                    </Avatar>
                    <Paper
                      elevation={1}
                      sx={{
                        p: 1.5,
                        bgcolor: message.sender === 'user' ? 'primary.light' : 'grey.100',
                        color: message.sender === 'user' ? 'white' : 'text.primary',
                        borderRadius: 2,
                      }}
                    >
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                        {message.text}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          opacity: 0.7,
                          display: 'block',
                          mt: 0.5,
                          textAlign: message.sender === 'user' ? 'right' : 'left',
                        }}
                      >
                        {formatTime(message.timestamp)}
                      </Typography>
                    </Paper>
                  </Box>
                </ListItem>
              ))}
              {isLoading && (
                <ListItem sx={{ justifyContent: 'center' }}>
                  <CircularProgress size={20} />
                  <Typography variant="caption" sx={{ ml: 1 }}>
                    AI is thinking...
                  </Typography>
                </ListItem>
              )}
            </List>
            <div ref={messagesEndRef} />
          </Box>

          <Divider />

          {/* Input */}
          <Box sx={{ p: 1, display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Ask about investments, goals, expenses..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage(inputText);
                }
              }}
              multiline
              maxRows={3}
            />
            <IconButton
              color="primary"
              onClick={startVoiceRecognition}
              disabled={isListening}
              sx={{ alignSelf: 'flex-end' }}
            >
              <MicIcon sx={{ color: isListening ? 'error.main' : 'primary.main' }} />
            </IconButton>
            <IconButton
              color="primary"
              onClick={() => handleSendMessage(inputText)}
              disabled={!inputText.trim() || isLoading}
              sx={{ alignSelf: 'flex-end' }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Collapse>
    </>
  );
};

export default ChatBot;
