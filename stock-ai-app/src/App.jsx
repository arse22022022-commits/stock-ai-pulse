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
  X,
  BookOpen,
  FileText
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

const REGIME_INFO = {
  0: { label: 'Estable', color: '#38bdf8', desc: 'Baja volatilidad y retornos neutrales.' },
  1: { label: 'Alcista', color: '#10b981', desc: 'Tendencia positiva con volatilidad controlada.' },
  2: { label: 'Volátil', color: '#ef4444', desc: 'Alta incertidumbre y posibles correcciones.' }
};

const getRegime = (id) => REGIME_INFO[id] || { label: 'Desconocido', color: '#94a3b8' };

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const isForecast = data.type === 'forecast';
    const regime = getRegime(data.regime);
    return (
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', padding: '12px', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.4)' }}>
        <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>{data.date}</p>
        <p style={{ margin: '4px 0 0', fontSize: '16px', fontWeight: 700, color: isForecast ? '#818cf8' : '#38bdf8' }}>
          ${data.price ? data.price.toFixed(2) : '0.00'}
          {isForecast && <span style={{ fontSize: '10px', marginLeft: '6px', opacity: 0.8 }}>(Forecast)</span>}
        </p>
        {data.regime !== undefined && (
          <p style={{ margin: '4px 0 0', fontSize: '11px', color: regime.color }}>
            Estado: {regime.label}
          </p>
        )}
      </div>
    );
  }
  return null;
};

const InterpretationGuide = ({ onClose }) => (
  <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(2, 6, 23, 0.85)', backdropFilter: 'blur(8px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
    <div className="guide-modal" style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '24px', width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto', padding: '40px', position: 'relative' }}>
      <button onClick={onClose} style={{ position: 'absolute', right: '24px', top: '24px', background: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
        <X style={{ width: '24px', height: '24px' }} />
      </button>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '32px' }}>
        <BookOpen style={{ width: '32px', height: '32px', color: '#38bdf8' }} />
        <h2 style={{ fontSize: '2rem', fontWeight: 700, margin: 0 }}>Guía de Interpretación</h2>
      </div>

      <section style={{ marginBottom: '32px' }}>
        <h3 style={{ color: '#38bdf8', marginBottom: '16px', fontSize: '1.25rem' }}>1. El Sistema de Consenso</h3>
        <p style={{ color: '#94a3b8', lineHeight: 1.6 }}>La IA no adivina; vota basándose en tres capas analíticas:</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '16px' }}>
          <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
            <h4 style={{ color: '#f8fafc', marginBottom: '8px' }}>Estructural</h4>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: 0 }}>Define el "clima" general del mercado (Alcista, Estable o Volátil).</p>
          </div>
          <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
            <h4 style={{ color: '#f8fafc', marginBottom: '8px' }}>Impulso</h4>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: 0 }}>Analiza la aceleración y "salud técnica" del movimiento actual.</p>
          </div>
          <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
            <h4 style={{ color: '#f8fafc', marginBottom: '8px' }}>Predictiva</h4>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: 0 }}>Proyecciones a 10 días mediante redes neuronales (Deep Learning).</p>
          </div>
        </div>
      </section>

      <section style={{ marginBottom: '32px' }}>
        <h3 style={{ color: '#38bdf8', marginBottom: '16px', fontSize: '1.25rem' }}>2. Diccionario de Alertas 🔍</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {[
            { tag: 'Impulso incipiente', desc: 'El movimiento positivo es muy joven (< 3 días). Puede ser ruido pasajero.', action: 'Esperar confirmación de 24-48h.' },
            { tag: 'Señales de agotamiento', desc: 'La confianza del modelo matemático está cayendo a pesar de la subida.', action: 'Vigilancia estrecha o recogida de beneficios.' },
            { tag: 'Riesgo de sobre-extensión', desc: 'El precio se ha alejado demasiado (>8%) de su media de 20 días.', action: 'Evitar comprar ahora; esperar corrección.' },
            { tag: 'Divergencia detectada', desc: 'El precio sube pero el impulso (aceleración) cae o es inestable.', action: 'Alerta máxima; suele preceder a caídas.' },
            { tag: 'Deriva negativa', desc: 'Fase estable sin volatilidad, pero con tendencia a gotear a la baja.', action: 'Falta de interés comprador.' }
          ].map((item, i) => (
            <div key={i} style={{ padding: '16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ color: '#fbbf24', fontWeight: 700, fontSize: '0.9rem' }}>{item.tag}</span>
                <span style={{ color: '#10b981', fontSize: '0.75rem', fontWeight: 600 }}>Acción: {item.action}</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: 0 }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
        <button onClick={() => window.print()} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', padding: '12px 24px', borderRadius: '12px', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
          <FileText style={{ width: '18px' }} /> Descargar / Imprimir Guía (PDF)
        </button>
      </div>
    </div>
  </div>
);

const App = () => {
  const [ticker, setTicker] = useState('NVDA');
  const [data, setData] = useState([]);
  const [price, setPrice] = useState(0);
  const [changePct, setChangePct] = useState(0);
  const [recommendation, setRecommendation] = useState(null);
  const [currentRegime, setCurrentRegime] = useState(0);
  const [currentRegimeDiff, setCurrentRegimeDiff] = useState(0);
  const [probsRet, setProbsRet] = useState([0, 0, 0]);
  const [probsDiff, setProbsDiff] = useState([0, 0, 0]);
  const [stateStatsRet, setStateStatsRet] = useState([]);
  const [stateStatsDiff, setStateStatsDiff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [showGuide, setShowGuide] = useState(false);

  const fetchData = async (symbol) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const response = await fetch(`${API_URL}/api/analyze/${symbol}`);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error ${response.status}`);
      }

      const result = await response.json();

      const formattedHistory = (result.history || []).map(item => ({
        ...item,
        date: new Date(item.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
        historyPrice: item.price,
        forecastPrice: null
      }));

      const formattedForecast = (result.forecast || []).map(item => ({
        ...item,
        date: new Date(item.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
        historyPrice: null,
        forecastPrice: item.price
      }));

      if (formattedHistory.length > 0 && formattedForecast.length > 0) {
        formattedHistory[formattedHistory.length - 1].forecastPrice = formattedHistory[formattedHistory.length - 1].historyPrice;
      }

      setData([...formattedHistory, ...formattedForecast]);
      setPrice(result.current_price || 0);
      setChangePct(result.change_pct || 0);
      setRecommendation(result.recommendation);
      setCurrentRegime(result.current_regime_ret ?? 0);
      setCurrentRegimeDiff(result.current_regime_diff ?? 0);
      setProbsRet(result.regime_probs_ret || [0, 0, 0]);
      setProbsDiff(result.regime_probs_diff || [0, 0, 0]);
      setStateStatsRet(result.state_stats_ret || []);
      setStateStatsDiff(result.state_stats_diff || []);
    } catch (err) {
      console.error("Fetch Error:", err);
      setErrorMsg(err.message || "Error al conectar con la API.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData('NVDA');
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    const symbol = e.target[0].value.trim().toUpperCase();
    if (symbol) {
      setTicker(symbol);
      fetchData(symbol);
    }
  };

  const regRet = getRegime(currentRegime);
  const regDiff = getRegime(currentRegimeDiff);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#020617', color: '#f8fafc', padding: '0px' }}>
      {showGuide && <InterpretationGuide onClose={() => setShowGuide(false)} />}

      {/* Header */}
      <nav style={{ padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.05)', backgroundColor: 'rgba(2, 6, 23, 0.8)', sticky: 'top', zIndex: 50, backdropFilter: 'blur(10px)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <BrainCircuit style={{ width: '32px', height: '32px', color: '#38bdf8' }} />
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>StockAI Pulse</h1>
        </div>

        <form onSubmit={handleSearch} style={{ position: 'relative', width: '300px' }}>
          <input
            type="text"
            placeholder="Buscar Ticker..."
            style={{ width: '100%', padding: '12px 20px', borderRadius: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'white' }}
          />
        </form>

        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <button
            onClick={() => setShowGuide(true)}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '8px 16px', borderRadius: '12px', fontSize: '0.9rem', color: '#38bdf8' }}
          >
            <BookOpen style={{ width: '18px' }} /> Guía de Interpretación
          </button>
          <Settings style={{ width: '20px', color: '#94a3b8' }} />
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ maxWidth: '1600px', margin: '0 auto', padding: '32px', display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' }}>

        {/* Error Message */}
        {errorMsg && (
          <div style={{ gridColumn: 'span 12', padding: '16px', borderRadius: '12px', border: '1px solid #ef4444', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', textAlign: 'center' }}>
            {errorMsg}
          </div>
        )}

        {/* Market Status Overview */}
        <div style={{ gridColumn: 'span 8', padding: '24px', borderRadius: '24px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <div>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '4px' }}>Precio en vivo ({ticker})</p>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                <h2 style={{ fontSize: '2.5rem', fontWeight: 700, margin: 0 }}>${price ? price.toFixed(2) : '0.00'}</h2>
                <span style={{ color: (changePct || 0) >= 0 ? '#10b981' : '#ef4444', fontWeight: 600 }}>
                  {(changePct || 0) >= 0 ? '+' : ''}{(changePct || 0).toFixed(2)}%
                </span>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <span style={{ padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 600, backgroundColor: `${regRet.color}20`, color: regRet.color, border: `1px solid ${regRet.color}40` }}>
                HMM Rep: {regRet.label}
              </span>
              <span style={{ padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 600, backgroundColor: `${regDiff.color}20`, color: regDiff.color, border: `1px solid ${regDiff.color}40` }}>
                HMM Diff: {regDiff.label}
              </span>
            </div>
          </div>

          {/* AI Recommendation Banner */}
          {recommendation && !loading && (
            <div style={{ marginBottom: '24px', padding: '16px 20px', borderRadius: '16px', background: `${recommendation.color}15`, border: `1px solid ${recommendation.color}40`, display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div style={{ background: recommendation.color, color: '#fff', padding: '8px 16px', borderRadius: '8px', fontWeight: 800, fontSize: '0.8rem' }}>
                {recommendation.verdict}
              </div>
              <p style={{ fontSize: '0.95rem', margin: 0 }}>{recommendation.reason}</p>
            </div>
          )}

          <div style={{ height: '400px', width: '100%', position: 'relative' }}>
            {loading && (
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(2, 6, 23, 0.6)', borderRadius: '12px', zIndex: 10 }}>
                <div style={{ width: '40px', height: '40px', border: '4px solid #38bdf8', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
              </div>
            )}
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" fontSize={10} />
                <YAxis hide={true} domain={['auto', 'auto']} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="historyPrice" stroke="#38bdf8" strokeWidth={3} fillOpacity={0.1} fill="#38bdf8" />
                <Area type="monotone" dataKey="forecastPrice" stroke="#818cf8" strokeWidth={3} strokeDasharray="5 5" fillOpacity={0.1} fill="#818cf8" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Side Panels */}
        <div style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ padding: '24px', borderRadius: '24px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Zap style={{ color: '#f59e0b' }} /> IA Insight (Rendimientos)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[0, 1, 2].map(id => {
                const item = REGIME_INFO[id];
                const stats = stateStatsRet.find(s => s.regime === id) || { mean: 0, std: 0 };
                const prob = ((probsRet[id] || 0) * 100).toFixed(1);
                const isCurrent = currentRegime === id;
                return (
                  <div key={id} style={{ padding: '12px', borderRadius: '12px', background: isCurrent ? `${item.color}15` : 'transparent', border: isCurrent ? `1px solid ${item.color}40` : '1px solid transparent' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: item.color }}>{item.label} ({prob}%)</span>
                      {isCurrent && <span style={{ fontSize: '10px', background: item.color, padding: '2px 6px', borderRadius: '4px' }}>ACTUAL</span>}
                    </div>
                    <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#94a3b8' }}>
                      <span>μ: {(stats.mean || 0).toFixed(3)}%</span>
                      <span>σ: {(stats.std || 0).toFixed(3)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ padding: '24px', borderRadius: '24px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart3 style={{ color: '#818cf8' }} /> IA Insight (Diferencias)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[0, 1, 2].map(id => {
                const item = REGIME_INFO[id];
                const stats = stateStatsDiff.find(s => s.regime === id) || { mean: 0, std: 0 };
                const prob = ((probsDiff[id] || 0) * 100).toFixed(1);
                const isCurrent = currentRegimeDiff === id;
                return (
                  <div key={id} style={{ padding: '12px', borderRadius: '12px', background: isCurrent ? `${item.color}15` : 'transparent', border: isCurrent ? `1px solid ${item.color}40` : '1px solid transparent' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: item.color }}>{item.label} ({prob}%)</span>
                      {isCurrent && <span style={{ fontSize: '10px', background: item.color, padding: '2px 6px', borderRadius: '4px' }}>ACTUAL</span>}
                    </div>
                    <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#94a3b8' }}>
                      <span>μ: {(stats.mean || 0).toFixed(3)}%</span>
                      <span>σ: {(stats.std || 0).toFixed(3)}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

      </main>

      <footer style={{ textAlign: 'center', padding: '40px', color: '#94a3b8', fontSize: '0.85rem' }}>
        <ShieldCheck style={{ width: '14px', marginRight: '8px' }} />
        Powered by Advanced HMM & Neural Forecasting Models
      </footer>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @media print {
          body * { visibility: hidden; }
          .guide-modal, .guide-modal * { visibility: visible; }
          .guide-modal { position: absolute; left: 0; top: 0; width: 100% !important; max-height: none !important; border: none !important; background: white !important; color: black !important; }
          .guide-modal h2, .guide-modal h3, .guide-modal h4 { color: black !important; }
          .guide-modal p, .guide-modal span { color: #333 !important; }
        }
      `}</style>
    </div>
  );
};

export default App;
