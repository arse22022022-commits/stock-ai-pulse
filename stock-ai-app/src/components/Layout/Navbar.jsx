import React from 'react';
import { BrainCircuit, BookOpen, Settings } from 'lucide-react';

export const Navbar = ({ activeTab, setActiveTab, handleSearch, setShowGuide }) => {
    return (
        <nav className="nav-container" style={{ padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.05)', backgroundColor: 'rgba(2, 6, 23, 0.8)', position: 'sticky', top: 0, zIndex: 100, backdropFilter: 'blur(10px)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }} className="nav-left">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <BrainCircuit style={{ width: '32px', height: '32px', color: '#38bdf8' }} />
                    <h1 className="logo-text" style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>StockAI Pulse</h1>
                </div>

                <div style={{ display: 'flex', gap: '4px', background: 'rgba(255,255,255,0.03)', padding: '4px', borderRadius: '12px' }} className="nav-tabs">
                    <button
                        onClick={() => setActiveTab('one-ticker')}
                        style={{ padding: '8px 16px', borderRadius: '8px', border: 'none', background: activeTab === 'one-ticker' ? '#38bdf8' : 'transparent', color: activeTab === 'one-ticker' ? '#020617' : '#94a3b8', fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s' }}
                    >
                        Análisis Ticker
                    </button>
                    <button
                        onClick={() => setActiveTab('portfolio')}
                        style={{ padding: '8px 16px', borderRadius: '8px', border: 'none', background: activeTab === 'portfolio' ? '#38bdf8' : 'transparent', color: activeTab === 'portfolio' ? '#020617' : '#94a3b8', fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s' }}
                    >
                        Análisis Cartera
                    </button>
                    <button
                        onClick={() => setActiveTab('indices')}
                        style={{ padding: '8px 16px', borderRadius: '8px', border: 'none', background: activeTab === 'indices' ? '#38bdf8' : 'transparent', color: activeTab === 'indices' ? '#020617' : '#94a3b8', fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s' }}
                    >
                        Índices Globales
                    </button>
                </div>
            </div>

            <form onSubmit={handleSearch} className="nav-search" style={{ position: 'relative', width: '300px' }}>
                <input
                    type="text"
                    placeholder={activeTab === 'one-ticker' ? "Buscar Ticker..." : "Añadir a Cartera..."}
                    style={{ width: '100%', padding: '12px 20px', borderRadius: '12px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: 'white' }}
                />
            </form>

            <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }} className="nav-right">
                <button
                    onClick={() => setShowGuide(true)}
                    className="guide-btn"
                    style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', padding: '8px 16px', borderRadius: '12px', fontSize: '0.9rem', color: '#38bdf8' }}
                >
                    <BookOpen style={{ width: '18px' }} /> <span className="guide-text">Guía de Interpretación</span>
                </button>
                <Settings style={{ width: '20px', color: '#94a3b8' }} />
            </div>
        </nav>
    );
};
