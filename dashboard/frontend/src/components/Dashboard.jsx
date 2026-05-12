// src/components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Avatar,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  AppBar,
  Toolbar,
  useTheme
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Timeline,
  PieChart as PieChartIcon,
  BarChart,
  Refresh,
  Twitter,
  ShowChart,
  AccountBalance,
  NotificationsActive
} from '@mui/icons-material';
import { Line, Pie, Bar } from 'recharts';
import axios from 'axios';
import { motion } from 'framer-motion';
import CountUp from 'react-countup';
import { useInView } from 'react-intersection-observer';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard = () => {
  const theme = useTheme();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [ref, inView] = useInView({ threshold: 0.3 });

  // Sample data for initial display
  const sampleStocks = [
    { symbol: 'TSLA', sentiment: 0.75, volume: 5432, change: 2.3 },
    { symbol: 'AAPL', sentiment: 0.62, volume: 3891, change: 1.1 },
    { symbol: 'MSFT', sentiment: 0.58, volume: 4256, change: 0.8 },
    { symbol: 'GOOGL', sentiment: -0.23, volume: 2987, change: -1.2 },
    { symbol: 'AMZN', sentiment: 0.31, volume: 3678, change: 0.5 },
    { symbol: 'META', sentiment: -0.45, volume: 4123, change: -2.1 },
    { symbol: 'NVDA', sentiment: 0.82, volume: 6789, change: 4.5 },
  ];

  const sentimentData = [
    { name: 'Positive', value: 45, color: '#4caf50' },
    { name: 'Negative', value: 25, color: '#f44336' },
    { name: 'Neutral', value: 30, color: '#ff9800' }
  ];

  const timelineData = [
    { time: '09:30', TSLA: 0.6, AAPL: 0.4, MSFT: 0.5 },
    { time: '10:00', TSLA: 0.7, AAPL: 0.5, MSFT: 0.4 },
    { time: '10:30', TSLA: 0.8, AAPL: 0.3, MSFT: 0.6 },
    { time: '11:00', TSLA: 0.5, AAPL: 0.6, MSFT: 0.7 },
    { time: '11:30', TSLA: 0.7, AAPL: 0.5, MSFT: 0.5 },
    { time: '12:00', TSLA: 0.9, AAPL: 0.7, MSFT: 0.6 },
  ];

  // Fetch real data from your API
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/dashboard`);
      setData(response.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.log('Using sample data (API not connected)');
      // Keep using sample data if API not available
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography variant="h6" align="center" sx={{ mt: 2 }}>
          Loading Market Dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="static" color="transparent" elevation={1}>
        <Toolbar>
          <ShowChart sx={{ mr: 2, color: theme.palette.primary.main }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Stock Sentiment Dashboard
          </Typography>
          <Chip 
            icon={<Refresh />} 
            label={`Last updated: ${lastUpdated.toLocaleTimeString()}`}
            variant="outlined"
            size="small"
            sx={{ mr: 2 }}
          />
          <Tooltip title="Live Updates Active">
            <Chip 
              icon={<NotificationsActive />} 
              label="LIVE" 
              color="success" 
              size="small"
            />
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* KPI Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card elevation={3}>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Stocks
                  </Typography>
                  <Typography variant="h3" component="div">
                    <CountUp end={sampleStocks.length} duration={2} />
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    actively tracked
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card elevation={3}>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Sentiment
                  </Typography>
                  <Typography variant="h3" component="div" color="success.main">
                    <CountUp end={0.65} decimals={2} duration={2} />
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    bullish trend
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card elevation={3}>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Tweets/Hour
                  </Typography>
                  <Typography variant="h3" component="div">
                    <CountUp end={28456} separator="," duration={2} />
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    +12% from yesterday
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Card elevation={3}>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Market Status
                  </Typography>
                  <Typography variant="h5" component="div" color="success.main">
                    BULLISH
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    65% positive sentiment
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </Grid>

        {/* Charts Section */}
        <Grid container spacing={3}>
          {/* Sentiment Timeline */}
          <Grid item xs={12} md={8}>
            <motion.div
              ref={ref}
              initial={{ opacity: 0, x: -20 }}
              animate={inView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.6 }}
            >
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Real-time Sentiment Trend
                </Typography>
                <Line
                  width={700}
                  height={300}
                  data={timelineData}
                  margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                >
                  <Line type="monotone" dataKey="TSLA" stroke="#8884d8" />
                  <Line type="monotone" dataKey="AAPL" stroke="#82ca9d" />
                  <Line type="monotone" dataKey="MSFT" stroke="#ffc658" />
                </Line>
              </Paper>
            </motion.div>
          </Grid>

          {/* Sentiment Distribution */}
          <Grid item xs={12} md={4}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={inView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  <PieChartIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Sentiment Distribution
                </Typography>
                <Pie
                  width={300}
                  height={300}
                  data={sentimentData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  label
                />
              </Paper>
            </motion.div>
          </Grid>

          {/* Stock Table */}
          <Grid item xs={12}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  <BarChart sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Stock Sentiment Overview
                </Typography>
                
                <Grid container spacing={2}>
                  {sampleStocks.map((stock, index) => (
                    <Grid item xs={12} key={stock.symbol}>
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <Paper 
                          variant="outlined" 
                          sx={{ 
                            p: 2,
                            '&:hover': {
                              boxShadow: 3,
                              cursor: 'pointer'
                            }
                          }}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar 
                              sx={{ 
                                bgcolor: stock.sentiment > 0.3 ? 'success.main' : 
                                       stock.sentiment < -0.3 ? 'error.main' : 'warning.main',
                                mr: 2
                              }}
                            >
                              {stock.symbol[0]}
                            </Avatar>
                            
                            <Box sx={{ flexGrow: 1 }}>
                              <Typography variant="subtitle1">
                                {stock.symbol}
                              </Typography>
                              <LinearProgress 
                                variant="determinate" 
                                value={(stock.volume / 7000) * 100}
                                sx={{ 
                                  height: 8, 
                                  borderRadius: 4,
                                  bgcolor: 'grey.200',
                                  '& .MuiLinearProgress-bar': {
                                    bgcolor: stock.sentiment > 0 ? 'success.main' : 'error.main'
                                  }
                                }}
                              />
                            </Box>
                            
                            <Box sx={{ textAlign: 'right', ml: 2 }}>
                              <Typography variant="h6">
                                {(stock.sentiment * 100).toFixed(1)}%
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                {stock.sentiment > 0 ? (
                                  <TrendingUp fontSize="small" color="success" />
                                ) : (
                                  <TrendingDown fontSize="small" color="error" />
                                )}
                                <Typography variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                                  {stock.volume.toLocaleString()} tweets
                                </Typography>
                              </Box>
                            </Box>
                          </Box>
                        </Paper>
                      </motion.div>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </motion.div>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard;