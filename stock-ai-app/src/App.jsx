import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Search,
  Settings,
  Zap,
  BarChart3,
  BrainCircuit,
  ShieldCheck,
  Info,
  Activity as ActivityIcon
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const REGIME_INFO = {
  0: { label: 'Estable', color: '#38bdf8', icon: <Activity />, desc: 'Baja volatilidad y retornos neutrales.' },
  1: { label: 'Alcista', color: '#10b981', icon: <TrendingUp />, desc: 'Tendencia positiva con volatilidad controlada.' },
  2: { label: 'Volátil', color: '#ef4444', icon: <Zap />, desc: 'Alta incertidumbre y posibles correcciones.' }
};

const App = () => {
  const [ticker, setTicker] = useState('NVDA');
  const [data, setData] = useState([]);
  const [price, setPrice] = useState(0);
  const [changePct, setChangePct] = useState(0);
  const [currentRegime, setCurrentRegime] = useState(1);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchData = async (symbol) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/analyze/${symbol}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();

      const formattedHistory = result.history.map(item => ({
        ...item,
        date: new Date(item.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
        historyPrice: item.price,
        forecastPrice: null
      }));

      const formattedForecast = result.forecast.map(item => ({
        ...item,
        date: new Date(item.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
        historyPrice: null,
        forecastPrice: item.price
      }));

      if (formattedHistory.length > 0 && formattedForecast.length > 0) {
        formattedHistory[formattedHistory.length - 1].forecastPrice = formattedHistory[formattedHistory.length - 1].historyPrice;
      }

      setData([...formattedHistory, ...formattedForecast]);
      setPrice(result.current_price);
      setChangePct(result.change_pct);
      setCurrentRegime(result.current_regime);
    } catch (err) {
      console.error("Error fetching data:", err);
      setErrorMsg("Error de conexión con el motor de IA.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData('NVDA');
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchData(ticker);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <nav style={{ padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="glass-card" style={{ padding: '8px', borderRadius: '12px' }}>
            <BrainCircuit className="gradient-text" style={{ width: '32px', height: '32px', color: '#38bdf8' }} />
          </div>
          <h1 className="gradient-text" style={{ fontSize: '1.5rem', fontWeight: 700 }}>StockAI Pulse</h1>
        </div>

        <form onSubmit={handleSearch} style={{ position: 'relative', width: '300px' }}>
          <Search style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)', width: '18px' }} />
          <input
            type="text"
            placeholder="Buscar Ticker (es. NVDA, AAPL)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            style={{ width: '100%', paddingLeft: '45px' }}
          />
        </form>

        <div style={{ display: 'flex', gap: '16px' }}>
          <button className="glass-card" style={{ padding: '10px', background: 'transparent' }}>
            <Settings style={{ width: '20px' }} />
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="dashboard-grid">

        {/* Market Status Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card col-span-8"
          style={{ padding: '24px', position: 'relative', overflow: 'hidden' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
            <div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '4px' }}>Precio en vivo ({ticker})</p>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                <h2 style={{ fontSize: '2.5rem', fontWeight: 700 }}>${price ? price.toFixed(2) : '---'}</h2>
                <span style={{
                  color: changePct >= 0 ? 'var(--success)' : 'var(--danger)',
                  display: 'flex',
                  alignItems: 'center',
                  fontWeight: 600
                }}>
                  {changePct >= 0 ? <TrendingUp style={{ width: '16px', marginRight: '4px' }} /> : <TrendingDown style={{ width: '16px', marginRight: '4px' }} />}
                  {changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%
                </span>
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '100px',
                backgroundColor: `${REGIME_INFO[currentRegime].color}20`,
                color: REGIME_INFO[currentRegime].color,
                border: `1px solid ${REGIME_INFO[currentRegime].color}40`,
                fontWeight: 600
              }}>
                {REGIME_INFO[currentRegime].icon}
                Estado: {REGIME_INFO[currentRegime].label}
              </div>
            </div>
          </div>

          <div style={{ height: '400px', width: '100%', position: 'relative' }}>
            {loading && (
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '12px', zIndex: 5, backdropFilter: 'blur(4px)' }}>
                <ActivityIcon className="animate-spin" style={{ color: 'var(--accent-primary)', width: '32px' }} />
              </div>
            )}

            {errorMsg && (
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px', zIndex: 5, color: 'var(--danger)', fontWeight: 600 }}>
                {errorMsg}
              </div>
            )}

            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent-primary)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="var(--accent-primary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                  minTickGap={30}
                />
                <YAxis
                  hide
                  domain={['auto', 'auto']}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-secondary)',
                    border: '1px solid var(--glass-border)',
                    borderRadius: '12px',
                    color: 'white'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="historyPrice"
                  stroke="var(--accent-primary)"
                  strokeWidth={3}
                  fillOpacity={1}
                  fill="url(#colorPrice)"
                  activeDot={{ r: 6 }}
                />
                <Area
                  type="monotone"
                  dataKey="forecastPrice"
                  stroke="var(--accent-secondary)"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  fillOpacity={0}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* AI Insight Sidepanel */}
        <div className="col-span-4" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card"
            style={{ padding: '24px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <Zap style={{ color: 'var(--warning)' }} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>IA Market Insight</h3>
            </div>
            <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6', fontSize: '0.95rem' }}>
              {REGIME_INFO[currentRegime].desc} El modelo detecta una transición hacia el <strong>Régimen {REGIME_INFO[currentRegime].label}</strong>.
            </p>
            <div style={{ marginTop: '20px', padding: '12px', borderRadius: '12px', backgroundColor: 'rgba(255,255,255,0.03)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Confianza del Modelo</span>
                <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>88%</span>
              </div>
              <div style={{ height: '6px', width: '100%', backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: '3px' }}>
                <div style={{ height: '100%', width: '88%', background: 'linear-gradient(90deg, #38bdf8, #818cf8)', borderRadius: '3px' }}></div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card"
            style={{ padding: '24px', flex: 1 }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
              <BarChart3 style={{ color: '#818cf8' }} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Probabilidades de Estado</h3>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {[
                { name: 'Alcista', prob: currentRegime === 1 ? 75 : 15, color: 'var(--success)' },
                { name: 'Estable', prob: currentRegime === 0 ? 75 : 15, color: 'var(--accent-primary)' },
                { name: 'Volátil', prob: currentRegime === 2 ? 75 : 10, color: 'var(--danger)' }
              ].map((item, idx) => (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontSize: '0.9rem' }}>{item.name}</span>
                    <span style={{ fontSize: '0.9rem', color: item.color, fontWeight: 600 }}>{item.prob}%</span>
                  </div>
                  <div style={{ height: '4px', width: '100%', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '2px' }}>
                    <div style={{ height: '100%', width: `${item.prob}%`, backgroundColor: item.color, borderRadius: '2px' }}></div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Technical Indicators Row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="col-span-full dashboard-grid"
          style={{ padding: 0 }}
        >
          {['RSI (14)', 'MACD', 'Moving Average', 'ATR'].map((tech, i) => (
            <div key={i} className="glass-card col-span-3" style={{ padding: '20px', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px' }}>{tech}</p>
              <div style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                {i === 0 ? '64.5' : i === 1 ? 'Neutral' : i === 2 ? 'Bullish' : '2.14'}
              </div>
            </div>
          ))}
        </motion.div>

      </main>

      {/* Footer */}
      <footer style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck style={{ width: '14px' }} />
          Powered by Advanced HMM & Neural Forecasting Models
        </div>
      </footer>
    </div>
  );
};

export default App;
