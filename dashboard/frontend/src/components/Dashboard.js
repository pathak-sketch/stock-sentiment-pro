import React, { useState } from 'react';
import {
    Container,
    Paper,
    TextField,
    Button,
    Grid,
    Card,
    CardContent,
    Typography,
    CircularProgress,
    Alert,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

function Dashboard() {
    const [stock, setStock] = useState('');
    const [sentiment, setSentiment] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const getSentimentLabel = (score) => {
        if (score === null || score === undefined) return 'N/A';
        if (score >= 0.2) return 'positive';
        if (score <= -0.2) return 'negative';
        return 'neutral';
    };

    const handleSearch = async () => {
        if (!stock.trim()) {
            setError('Please enter a stock symbol');
            return;
        }

        setLoading(true);
        setError(null);
        setSentiment(null);

        try {
            const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/sentiment/${stock.toUpperCase()}`);
            const data = await response.json();

            if (data.error) {
                throw new Error(`${data.error}${data.available ? ' Available: ' + data.available.join(', ') : ''}`);
            }

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to fetch sentiment data');
            }

            const score = data.summary?.avg_sentiment ?? data.score ?? null;
            const label = data.sentiment ?? getSentimentLabel(score);

            setSentiment({
                sentiment_score: score,
                sentiment_label: label,
            });
        } catch (err) {
            setError(err.message || 'Failed to fetch sentiment data. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Stock Sentiment Analyzer
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                    Analyze real-time sentiment for any stock symbol
                </Typography>

                <Grid container spacing={2}>
                    <Grid item xs={12} sm={9}>
                        <TextField
                            fullWidth
                            placeholder="Enter stock symbol (e.g., AAPL, GOOGL)"
                            value={stock}
                            onChange={(e) => setStock(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        />
                    </Grid>
                    <Grid item xs={12} sm={3}>
                        <Button
                            fullWidth
                            variant="contained"
                            color="primary"
                            onClick={handleSearch}
                            disabled={loading}
                            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                        >
                            {loading ? 'Analyzing...' : 'Analyze'}
                        </Button>
                    </Grid>
                </Grid>
            </Paper>

            {error && <Alert severity="error">{error}</Alert>}

            {sentiment && (
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                        <Card>
                            <CardContent>
                                <Typography color="textSecondary" gutterBottom>
                                    Sentiment Score
                                </Typography>
                                <Typography variant="h5" color="primary">
                                    {sentiment.sentiment_score !== null && sentiment.sentiment_score !== undefined
                                        ? sentiment.sentiment_score.toFixed(2)
                                        : 'N/A'}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <Card>
                            <CardContent>
                                <Typography color="textSecondary" gutterBottom>
                                    Sentiment Label
                                </Typography>
                                <Typography variant="h5" color="primary">
                                    {sentiment.sentiment_label || 'N/A'}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}
        </Container>
    );
}

export default Dashboard;
