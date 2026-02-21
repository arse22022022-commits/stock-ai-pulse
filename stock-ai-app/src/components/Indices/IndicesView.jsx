import React from 'react';
import { Globe, ChevronRight } from 'lucide-react';
import { AssetCard } from '../Portfolio/AssetCard';
import { INDICES_CONSTITUENTS } from '../../data/indices';

export const IndicesView = ({
    indicesData,
    indicesLoading,
    analyzeIndices,
    currentIndex,
    handleIndexSelect
}) => {
    return (
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

                            <div className="asset-grid">
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
    );
};
