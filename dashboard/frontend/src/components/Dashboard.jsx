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
  Tooltip,
  AppBar,
  Toolbar,
  useTheme
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Timeline,
  PieChart as PieChartIcon,
  BarChart,
  Refresh,
  ShowChart,
  NotificationsActive
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart as RechartsBarChart,
  Bar
} from 'recharts';
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
  const [ref, inView] = useInView({ threshold: 0.1 });
 
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
 
  const volumeData = sampleStocks.map(s => ({
    symbol: s.symbol,
    volume: s.volume,
    sentiment: parseFloat((s.sentiment * 100).toFixed(1))
  }));
 
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);
 
  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/dashboard`);
      setData(response.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.log('Using sample data (API not connected)');
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
    <Box sx={{ flexGrow: 1, bgcolor: '#f0f2f5', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="static" sx={{ bgcolor: '#1a1a2e' }} elevation={2}>
        <Toolbar>
          <ShowChart sx={{ mr: 2, color: '#00d4ff' }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold', color: '#fff' }}>
            Stock Sentiment Dashboard
          </Typography>
          <Chip
            icon={<Refresh sx={{ color: '#fff !important' }} />}
            label={`Updated: ${lastUpdated.toLocaleTimeString()}`}
            variant="outlined"
            size="small"
            sx={{ mr: 2, color: '#fff', borderColor: '#ffffff44' }}
          />
          <Chip
            icon={<NotificationsActive />}
            label="LIVE"
            color="success"
            size="small"
          />
        </Toolbar>
      </AppBar>
 
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* KPI Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {[
            { label: 'Total Stocks', value: sampleStocks.length, suffix: '', sub: 'actively tracked', color: '#1976d2', decimals: 0 },
            { label: 'Avg Sentiment', value: 0.65, suffix: '', sub: 'bullish trend', color: '#4caf50', decimals: 2 },
            { label: 'Tweets / Hour', value: 28456, suffix: '', sub: '+12% from yesterday', color: '#9c27b0', decimals: 0, separator: ',' },
            { label: 'Market Status', value: null, sub: '65% positive sentiment', color: '#4caf50', isText: true },
          ].map((kpi, i) => (
            <Grid item xs={12} sm={6} md={3} key={kpi.label}>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                <Card elevation={3} sx={{ borderTop: `4px solid ${kpi.color}` }}>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom fontSize={13}>
                      {kpi.label}
                    </Typography>
                    {kpi.isText ? (
                      <Typography variant="h5" fontWeight="bold" color="success.main">BULLISH</Typography>
                    ) : (
                      <Typography variant="h3" fontWeight="bold" color={kpi.color}>
                        <CountUp end={kpi.value} decimals={kpi.decimals} duration={2} separator={kpi.separator || ''} />
                      </Typography>
                    )}
                    <Typography variant="body2" color="textSecondary" mt={0.5}>{kpi.sub}</Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
 
        <Grid container spacing={3}>
          {/* Line Chart */}
          <Grid item xs={12} md={8}>
            <motion.div ref={ref} initial={{ opacity: 0, x: -20 }} animate={inView ? { opacity: 1, x: 0 } : {}} transition={{ duration: 0.6 }}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  <Timeline sx={{ mr: 1, verticalAlign: 'middle', color: '#1976d2' }} />
                  Real-time Sentiment Trend
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={timelineData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis dataKey="time" />
                    <YAxis domain={[0, 1]} tickFormatter={v => `${(v * 100).toFixed(0)}%`} />
                    <RechartsTooltip formatter={(v) => `${(v * 100).toFixed(1)}%`} />
                    <Legend />
                    <Line type="monotone" dataKey="TSLA" stroke="#8884d8" strokeWidth={2} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="AAPL" stroke="#82ca9d" strokeWidth={2} dot={{ r: 4 }} />
                    <Line type="monotone" dataKey="MSFT" stroke="#ffc658" strokeWidth={2} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </Paper>
            </motion.div>
          </Grid>
 
          {/* Pie Chart */}
          <Grid item xs={12} md={4}>
            <motion.div initial={{ opacity: 0, x: 20 }} animate={inView ? { opacity: 1, x: 0 } : {}} transition={{ duration: 0.6, delay: 0.2 }}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  <PieChartIcon sx={{ mr: 1, verticalAlign: 'middle', color: '#9c27b0' }} />
                  Sentiment Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {sentimentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip formatter={(v) => `${v}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </motion.div>
          </Grid>
 
          {/* Bar Chart */}
          <Grid item xs={12} md={6}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={inView ? { opacity: 1, y: 0 } : {}} transition={{ duration: 0.6, delay: 0.3 }}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  <BarChart sx={{ mr: 1, verticalAlign: 'middle', color: '#f44336' }} />
                  Tweet Volume by Stock
                </Typography>
                <ResponsiveContainer width="100%" height={250}>
                  <RechartsBarChart data={volumeData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                    <XAxis dataKey="symbol" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="volume" fill="#1976d2" radius={[4, 4, 0, 0]} />
                  </RechartsBarChart>
                </ResponsiveContainer>
              </Paper>
            </motion.div>
          </Grid>
 
          {/* Stock List */}
          <Grid item xs={12} md={6}>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={inView ? { opacity: 1, y: 0 } : {}} transition={{ duration: 0.6, delay: 0.4 }}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  <BarChart sx={{ mr: 1, verticalAlign: 'middle', color: '#ff9800' }} />
                  Stock Sentiment Overview
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {sampleStocks.map((stock, index) => (
                    <motion.div
                      key={stock.symbol}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.07 }}
                    >
                      <Paper variant="outlined" sx={{ p: 1.5, '&:hover': { boxShadow: 3, cursor: 'pointer' } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{
                            width: 36, height: 36, fontSize: 14, fontWeight: 'bold',
                            bgcolor: stock.sentiment > 0.3 ? 'success.main' : stock.sentiment < -0.3 ? 'error.main' : 'warning.main'
                          }}>
                            {stock.symbol[0]}
                          </Avatar>
                          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                            <Typography variant="subtitle2" fontWeight="bold">{stock.symbol}</Typography>
                            <LinearProgress
                              variant="determinate"
                              value={(stock.volume / 7000) * 100}
                              sx={{
                                height: 6, borderRadius: 3, bgcolor: 'grey.200',
                                '& .MuiLinearProgress-bar': {
                                  bgcolor: stock.sentiment > 0 ? 'success.main' : 'error.main'
                                }
                              }}
                            />
                          </Box>
                          <Box sx={{ textAlign: 'right', minWidth: 70 }}>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {(stock.sentiment * 100).toFixed(1)}%
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                              {stock.sentiment > 0
                                ? <TrendingUp fontSize="small" color="success" />
                                : <TrendingDown fontSize="small" color="error" />}
                              <Typography variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>
                                {stock.volume.toLocaleString()}
                              </Typography>
                            </Box>
                          </Box>
                        </Box>
                      </Paper>
                    </motion.div>
                  ))}
                </Box>
              </Paper>
            </motion.div>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};
 
export default Dashboard;
 