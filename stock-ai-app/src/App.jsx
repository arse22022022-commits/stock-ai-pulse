import React, { useState } from 'react';
import { ShieldCheck } from 'lucide-react';

// Components
import { Navbar } from './components/Layout/Navbar';
import { InterpretationGuide } from './components/Modals/InterpretationGuide';
import { StockDashboard } from './components/Dashboard/StockDashboard';
import { AssetCard } from './components/Portfolio/AssetCard';

import { PortfolioView } from './components/Portfolio/PortfolioView';
import { IndicesView } from './components/Indices/IndicesView';

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
      <main className="main-content" style={{ maxWidth: '1600px', margin: '0 auto' }}>

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
          <PortfolioView
            portfolioTickers={portfolioTickers}
            portfolioData={portfolioData}
            portfolioLoading={portfolioLoading}
            removeTicker={removeTicker}
            analyzePortfolio={analyzePortfolio}
          />
        ) : (
          <IndicesView
            indicesData={indicesData}
            indicesLoading={indicesLoading}
            analyzeIndices={analyzeIndices}
            currentIndex={currentIndex}
            handleIndexSelect={handleIndexSelect}
          />
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
          .guide-modal { position: absolute; left: 0; top: 0; width: 100% !important; max-height: none !important; border: none !important; background: white !important; color: black !important; }
          .guide-modal h2, .guide-modal h3, .guide-modal h4 { color: black !important; }
          .guide-modal p, .guide-modal span { color: #333 !important; }
        }
      `}</style>
    </div>
  );
};

export default App;
