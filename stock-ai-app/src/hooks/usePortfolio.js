import { useState, useEffect, useCallback } from 'react';

const API_URL = import.meta.env.PROD
    ? ''
    : (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000');

export const usePortfolio = () => {
    const [portfolioTickers, setPortfolioTickers] = useState(() => {
        const saved = localStorage.getItem('portfolio_tickers');
        return saved ? JSON.parse(saved) : ['AAPL', 'MSFT', 'GOOG'];
    });

    const [portfolioData, setPortfolioData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Persistence
    useEffect(() => {
        localStorage.setItem('portfolio_tickers', JSON.stringify(portfolioTickers));
    }, [portfolioTickers]);

    const addTicker = (ticker) => {
        if (ticker && !portfolioTickers.includes(ticker)) {
            setPortfolioTickers(prev => [...prev, ticker]);
        }
    };

    const removeTicker = (ticker) => {
        setPortfolioTickers(prev => prev.filter(t => t !== ticker));
    };

    const analyzePortfolio = useCallback(async () => {
        if (portfolioTickers.length === 0) return;
        setLoading(true);
        setError(null);
        try {
            const resp = await fetch(`${API_URL}/api/portfolio`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(portfolioTickers)
            });
            if (!resp.ok) {
                const errData = await resp.json().catch(() => ({}));
                throw new Error(errData.detail || "Error al analizar la cartera.");
            }
            const result = await resp.json();
            setPortfolioData(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [portfolioTickers]);

    return {
        portfolioTickers,
        portfolioData,
        loading,
        error,
        addTicker,
        removeTicker,
        analyzePortfolio
    };
};
