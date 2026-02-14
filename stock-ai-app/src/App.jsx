import React, { useState } from 'react';
import { ShieldCheck } from 'lucide-react';

// Components
import { Navbar } from './components/Layout/Navbar';
import { InterpretationGuide } from './components/Modals/InterpretationGuide';
import { StockDashboard } from './components/Dashboard/StockDashboard';
import { AssetCard } from './components/Portfolio/AssetCard';

// Hooks
import { useStockData } from './hooks/useStockData';
import { usePortfolio } from './hooks/usePortfolio';
import { useIndices } from './hooks/useIndices';

// Data
import { INDICES_CONSTITUENTS } from './data/indices';

// Icons
import { Activity, Briefcase, Trash2, PieChart, BrainCircuit, Globe, ChevronRight } from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('one-ticker'); // 'one-ticker', 'portfolio', 'indices'
  const [ticker, setTicker] = useState('NVDA');
  const [showGuide, setShowGuide] = useState(false);

  // Hooks
  const { data, metrics, loading, error: singleError } = useStockData(ticker);
  const {
    portfolioTickers,
    portfolioData,
    loading: portfolioLoading,
    error: portfolioError,
    addTicker,
    removeTicker,
    analyzePortfolio
  } = usePortfolio();

  const {
    indicesData,
    loading: indicesLoading,
    error: indicesError,
    analyzeIndices,
    currentIndex
  } = useIndices();

  const handleSearch = (e) => {
    e.preventDefault();
    const symbol = e.target[0].value.trim().toUpperCase();
    if (symbol) {
      if (activeTab === 'one-ticker') {
        setTicker(symbol);
      } else {
        addTicker(symbol);
        e.target[0].value = '';
      }
    }
  };

  const handleIndexSelect = (indexName) => {
    const tickers = INDICES_CONSTITUENTS[indexName];
    analyzeIndices(tickers, indexName);
  };

  const errorMsg = singleError || portfolioError || indicesError;

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#020617', color: '#f8fafc', padding: '0px' }}>
      {showGuide && <InterpretationGuide onClose={() => setShowGuide(false)} />}

      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        handleSearch={handleSearch}
        setShowGuide={setShowGuide}
      />

      {/* Main Content */}
      <main style={{ maxWidth: '1600px', margin: '0 auto', padding: '32px' }}>

        {/* Error Message */}
        {errorMsg && (
          <div style={{ padding: '16px', borderRadius: '12px', border: '1px solid #ef4444', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', textAlign: 'center', marginBottom: '24px' }}>
            {errorMsg}
          </div>
        )}

        {activeTab === 'one-ticker' ? (
          <StockDashboard
            ticker={ticker}
            data={data}
            metrics={metrics}
            loading={loading}
          />
        ) : activeTab === 'portfolio' ? (
          /* Portfolio Section */
          <div className="main-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' }}>
            <div className="portfolio-sidebar" style={{ gridColumn: 'span 3' }}>
              <div style={{ padding: '24px', borderRadius: '24px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)', height: 'fit-content' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
                  <Briefcase style={{ color: '#38bdf8' }} />
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0 }}>Constituir Cartera</h3>
                </div>

                <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '16px' }}>Gestione los activos de su cartera individualmente.</p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
                  {portfolioTickers.map(t => (
                    <div key={t} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <span style={{ fontWeight: 700 }}>{t}</span>
                      <button onClick={() => removeTicker(t)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer' }}>
                        <Trash2 style={{ width: '18px' }} />
                      </button>
                    </div>
                  ))}
                  {portfolioTickers.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '20px', color: '#64748b', fontSize: '0.9rem', border: '1px dashed #334155', borderRadius: '12px' }}>
                      No hay activos registrados. Use el buscador superior para añadir.
                    </div>
                  )}
                </div>

                <button
                  onClick={analyzePortfolio}
                  disabled={portfolioLoading || portfolioTickers.length === 0}
                  style={{ width: '100%', padding: '16px', borderRadius: '14px', background: '#38bdf8', color: '#020617', fontWeight: 800, border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px' }}
                >
                  {portfolioLoading ? <div style={{ width: '20px', height: '20px', border: '2px solid #000', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div> : <Activity style={{ width: '20px' }} />}
                  ANÁLISIS DE LA CARTERA
                </button>
              </div>
            </div>

            <div className="portfolio-content" style={{ gridColumn: 'span 9' }}>
              <div style={{ padding: '32px', borderRadius: '24px', background: 'rgba(15, 23, 42, 0.4)', border: '1px solid rgba(255,255,255,0.05)', minHeight: '500px' }}>
                {!portfolioData && !portfolioLoading && (
                  <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', opacity: 0.6 }}>
                    <PieChart style={{ width: '80px', height: '80px', marginBottom: '24px', color: '#64748b' }} />
                    <h4 style={{ fontSize: '1.4rem', fontWeight: 600, margin: '0 0 12px' }}>Esperando Ejecución</h4>
                    <p style={{ maxWidth: '400px', lineHeight: 1.6 }}>Configure sus activos a la izquierda y pulse el botón para iniciar el análisis multidimensional de su cartera.</p>
                  </div>
                )}

                {portfolioLoading && (
                  <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                    <div style={{ width: '64px', height: '64px', border: '4px solid #38bdf8', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite', marginBottom: '24px' }}></div>
                    <h4 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Sincronizando Modelos HMM...</h4>
                    <p style={{ color: '#94a3b8' }}>Este proceso puede tardar unos segundos dependiendo del número de activos.</p>
                  </div>
                )}

                {portfolioData && !portfolioLoading && (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                      <h3 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800 }}>Veredicto Agregado IA</h3>
                      <div style={{ padding: '8px 20px', borderRadius: '20px', background: portfolioData.summary.risk_level === 'Alto' ? '#ef444420' : '#10b98120', border: '1px solid ' + (portfolioData.summary.risk_level === 'Alto' ? '#ef444440' : '#10b98140'), color: portfolioData.summary.risk_level === 'Alto' ? '#ef4444' : '#10b981', fontWeight: 800, fontSize: '0.8rem' }}>
                        RIESGO: {portfolioData.summary.risk_level.toUpperCase()}
                      </div>
                    </div>

                    <div style={{ padding: '24px', borderRadius: '20px', background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(15, 23, 42, 1) 100%)', border: '1px solid rgba(56, 189, 248, 0.2)', marginBottom: '32px' }}>
                      <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                        <BrainCircuit style={{ width: '28px', color: '#38bdf8', marginTop: '4px' }} />
                        <p style={{ margin: 0, fontSize: '1.1rem', lineHeight: 1.6, fontWeight: 500 }}>{portfolioData.summary.advice}</p>
                      </div>
                    </div>

                    <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '20px', color: '#94a3b8' }}>DESGLOSE TÉCNICO POR ACTIVO</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                      {[...portfolioData.assets]
                        .sort((a, b) => {
                          const rank = {
                            'COMPRA FUERTE': 5,
                            'COMPRA': 4,
                            'MANTENER': 3,
                            'VENTA': 2,
                            'VENTA FUERTE': 1
                          };
                          const scoreA = rank[a.recommendation.verdict] || 0;
                          const scoreB = rank[b.recommendation.verdict] || 0;

                          if (scoreA !== scoreB) {
                            return scoreB - scoreA;
                          }

                          const meanA = a.state_stats_ret?.find(s => s.regime === a.current_regime_ret)?.mean || 0;
                          const meanB = b.state_stats_ret?.find(s => s.regime === b.current_regime_ret)?.mean || 0;
                          return meanB - meanA;
                        })
                        .map(asset => (
                          <AssetCard key={asset.ticker} asset={asset} />
                        ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Indices Constituents Section */
          <div className="main-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' }}>
            {/* Indices Selector Sidebar */}
            <div className="indices-sidebar" style={{ gridColumn: 'span 3' }}>
              <div style={{ padding: '24px', borderRadius: '24px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)', height: 'fit-content' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
                  <Globe style={{ color: '#38bdf8' }} />
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0 }}>Seleccionar Índice</h3>
                </div>

                <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '24px' }}>
                  Analice los componentes de los principales índices mundiales.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {Object.keys(INDICES_CONSTITUENTS).map(indexName => (
                    <button
                      key={indexName}
                      onClick={() => handleIndexSelect(indexName)}
                      disabled={indicesLoading}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '16px',
                        borderRadius: '12px',
                        border: currentIndex === indexName ? '1px solid #38bdf8' : '1px solid rgba(255,255,255,0.05)',
                        background: currentIndex === indexName ? 'rgba(56, 189, 248, 0.1)' : 'rgba(255,255,255,0.03)',
                        color: currentIndex === indexName ? '#38bdf8' : '#cbd5e1',
                        cursor: 'pointer',
                        textAlign: 'left',
                        fontWeight: 600,
                        transition: 'all 0.2s'
                      }}
                    >
                      {indexName}
                      <ChevronRight style={{ width: '16px', opacity: currentIndex === indexName ? 1 : 0.5 }} />
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Indices Results Content */}
            <div className="indices-content" style={{ gridColumn: 'span 9' }}>
              <div style={{ padding: '32px', borderRadius: '24px', background: 'rgba(15, 23, 42, 0.4)', border: '1px solid rgba(255,255,255,0.05)', minHeight: '500px' }}>

                {!indicesData && !indicesLoading && (
                  <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', opacity: 0.6 }}>
                    <Globe style={{ width: '80px', height: '80px', marginBottom: '24px', color: '#64748b' }} />
                    <h4 style={{ fontSize: '1.4rem', fontWeight: 600, margin: '0 0 12px' }}>Seleccione un Índice</h4>
                    <p style={{ maxWidth: '400px', lineHeight: 1.6 }}>
                      Elija un índice del menú lateral para analizar todos sus componentes y detectar oportunidades de <strong>COMPRA FUERTE</strong>.
                    </p>
                  </div>
                )}

                {indicesLoading && (
                  <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                    <div style={{ width: '64px', height: '64px', border: '4px solid #38bdf8', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite', marginBottom: '24px' }}></div>
                    <h4 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Analizando {currentIndex}...</h4>
                    <p style={{ color: '#94a3b8' }}>Procesando modelos HMM para todos los componentes.</p>
                  </div>
                )}

                {indicesData && !indicesLoading && (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                      <div>
                        <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: 0 }}>Oportunidades en {currentIndex}</h2>
                        <p style={{ color: '#94a3b8', margin: '4px 0 0' }}>Filtrando por <strong>COMPRA FUERTE</strong></p>
                      </div>
                      <div style={{ padding: '8px 20px', borderRadius: '20px', background: '#38bdf820', border: '1px solid #38bdf840', color: '#38bdf8', fontWeight: 800, fontSize: '0.9rem' }}>
                        {indicesData.assets.filter(a => a.recommendation.verdict === 'COMPRA FUERTE').length} OPORTUNIDADES
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                      {indicesData.assets
                        .filter(a => a.recommendation.verdict === 'COMPRA FUERTE')
                        .sort((a, b) => { // Sort by HMM Mean Descending
                          const meanA = a.state_stats_ret?.find(s => s.regime === a.current_regime_ret)?.mean || 0;
                          const meanB = b.state_stats_ret?.find(s => s.regime === b.current_regime_ret)?.mean || 0;
                          return meanB - meanA;
                        })
                        .map(asset => (
                          <AssetCard key={asset.ticker} asset={asset} />
                        ))}

                      {indicesData.assets.filter(a => a.recommendation.verdict === 'COMPRA FUERTE').length === 0 && (
                        <div style={{ gridColumn: 'span 3', padding: '60px', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '16px', border: '1px dashed rgba(255,255,255,0.1)' }}>
                          <p style={{ fontSize: '1.1rem', color: '#94a3b8', marginBottom: '8px' }}>No se han encontrado oportunidades claras.</p>
                          <p style={{ fontSize: '0.9rem', color: '#64748b' }}>Ningún activo del {currentIndex} presenta actualmente una señal de <strong>COMPRA FUERTE</strong>.</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

      </main>

      <footer style={{ textAlign: 'center', padding: '40px', color: '#94a3b8', fontSize: '0.85rem' }}>
        <ShieldCheck style={{ width: '14px', marginRight: '8px' }} />
        Powered by Advanced HMM & Neural Forecasting Models
      </footer>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        
        /* Mobile Responsive adjustments */
        @media (max-width: 1024px) {
          .nav-container { padding: 16px 20px !important; flex-wrap: wrap; gap: 16px; justify-content: center !important; }
          .nav-left { gap: 16px !important; width: 100%; justify-content: center; }
          .nav-search { width: 100% !important; order: 3; }
          .nav-right { order: 2; width: auto; }
          .main-grid { grid-template-columns: 1fr !important; }
          .chart-panel, .side-panels, .portfolio-sidebar, .portfolio-content, .indices-sidebar, .indices-content { grid-column: span 12 !important; }
        }

        @media (max-width: 640px) {
          .nav-left { flex-direction: column; gap: 12px !important; }
          .logo-text { font-size: 1.25rem !important; }
          .guide-text { display: none; }
          .main-content { padding: 16px !important; }
        }

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
