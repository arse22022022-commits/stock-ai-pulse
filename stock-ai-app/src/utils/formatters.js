export const REGIME_INFO = {
    0: { label: 'Estable', color: '#38bdf8', desc: 'Baja volatilidad y retornos neutrales.' },
    1: { label: 'Alcista', color: '#10b981', desc: 'Tendencia positiva con volatilidad controlada.' },
    2: { label: 'Volátil', color: '#ef4444', desc: 'Alta incertidumbre y posibles correcciones.' }
};

export const getRegime = (id) => REGIME_INFO[id] || { label: 'Desconocido', color: '#94a3b8' };

export const CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'CAD': 'C$',
    'AUD': 'A$',
    'CHF': 'CHF',
    'CNY': '¥'
};

export const getCurrencySymbol = (code) => CURRENCY_SYMBOLS[code] || code;
