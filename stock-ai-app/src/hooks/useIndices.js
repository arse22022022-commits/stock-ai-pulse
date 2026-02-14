import { useState, useCallback } from 'react';

const API_URL = import.meta.env.PROD
    ? ''
    : (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000');

export const useIndices = () => {
    const [indicesData, setIndicesData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [currentIndex, setCurrentIndex] = useState(null);

    const analyzeIndices = useCallback(async (tickers, indexName) => {
        if (!tickers || tickers.length === 0) return;

        setLoading(true);
        setError(null);
        setIndicesData(null);
        setCurrentIndex(indexName);

        try {
            const resp = await fetch(`${API_URL}/api/portfolio`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tickers)
            });
            if (!resp.ok) {
                const errData = await resp.json().catch(() => ({}));
                throw new Error(errData.detail || "Error al analizar componentes del índice.");
            }
            const result = await resp.json();
            setIndicesData(result);
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    return {
        indicesData,
        loading,
        error,
        analyzeIndices,
        currentIndex
    };
};
