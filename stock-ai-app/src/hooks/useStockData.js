import { useState, useEffect, useCallback } from 'react';

const API_URL = import.meta.env.PROD
    ? ''
    : (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000');

export const useStockData = (ticker) => {
    const [data, setData] = useState([]);
    const [metrics, setMetrics] = useState({
        price: 0,
        changePct: 0,
        currency: 'USD',
        recommendation: null,
        currentRegime: 0,
        currentRegimeDiff: 0,
        probsRet: [0, 0, 0],
        probsDiff: [0, 0, 0],
        stateStatsRet: [],
        stateStatsDiff: [],
        riskRewardRatio: null
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        if (!ticker) return;

        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/api/analyze/${ticker}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Error ${response.status}`);
            }

            const result = await response.json();

            const formattedHistory = (result.history || [])
                .slice(-65)
                .map(item => ({
                    ...item,
                    date: new Date(item.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
                    historyPrice: item.price,
                    forecastPrice: null,
                    range: null,
                    price_low: null,
                    price_high: null
                }));

            const formattedForecast = (result.forecast || []).map(item => ({
                ...item,
                date: new Date(item.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
                historyPrice: null,
                forecastPrice: item.price,
                range: [item.price_low, item.price_high],
                price_low: item.price_low,
                price_high: item.price_high
            }));

            // Stitching logic
            if (formattedHistory.length > 0 && formattedForecast.length > 0) {
                const lastPrice = formattedHistory[formattedHistory.length - 1].historyPrice;
                formattedHistory[formattedHistory.length - 1].forecastPrice = lastPrice;
                formattedHistory[formattedHistory.length - 1].range = [lastPrice, lastPrice];
                formattedHistory[formattedHistory.length - 1].price_low = lastPrice;
                formattedHistory[formattedHistory.length - 1].price_high = lastPrice;
            }

            setData([...formattedHistory, ...formattedForecast]);

            setMetrics({
                price: result.current_price || 0,
                changePct: result.change_pct || 0,
                currency: result.currency || 'USD',
                recommendation: result.recommendation,
                currentRegime: result.current_regime_ret ?? 0,
                currentRegimeDiff: result.current_regime_diff ?? 0,
                probsRet: result.regime_probs_ret || [0, 0, 0],
                probsDiff: result.regime_probs_diff || [0, 0, 0],
                stateStatsRet: result.state_stats_ret || [],
                stateStatsDiff: result.state_stats_diff || [],
                riskRewardRatio: result.risk_reward_ratio
            });

        } catch (err) {
            console.error("Fetch Error:", err);
            setError(err.message || "Error al conectar con la API.");
        } finally {
            setLoading(false);
        }
    }, [ticker]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return { data, metrics, loading, error, refetch: fetchData };
};
