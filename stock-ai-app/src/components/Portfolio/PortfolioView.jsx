import React from 'react';
import { Briefcase, Trash2, Activity, PieChart, BrainCircuit } from 'lucide-react';
import { AssetCard } from './AssetCard';

export const PortfolioView = ({
    portfolioTickers,
    portfolioData,
    portfolioLoading,
    removeTicker,
    analyzePortfolio
}) => {
    return (
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
                                <h3 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800 }}>Veredicto Agregado HMM</h3>
                                <div style={{ padding: '8px 20px', borderRadius: '20px', background: portfolioData.summary.risk_level === 'Alto' ? '#ef444420' : '#10b98120', border: '1px solid ' + (portfolioData.summary.risk_level === 'Alto' ? '#ef444440' : '#10b98140'), color: portfolioData.summary.risk_level === 'Alto' ? '#ef4444' : '#10b981', fontWeight: 800, fontSize: '0.8rem' }}>
                                    RIESGO: {portfolioData.summary.risk_level.toUpperCase()}
                                </div>
                            </div>

                            <div style={{ padding: '24px', borderRadius: '20px', background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(15, 23, 42, 1) 100%)', border: '1px solid rgba(56, 189, 248, 0.2)', marginBottom: '32px' }}>
                                <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                                    <Activity style={{ width: '28px', color: '#38bdf8', marginTop: '4px' }} />
                                    <p style={{ margin: 0, fontSize: '1.1rem', lineHeight: 1.6, fontWeight: 500 }}>{portfolioData.summary.advice}</p>
                                </div>
                            </div>

                            {/* Gemini AI Analyst Panel */}
                            {portfolioData.summary.ai_insight && (
                                <div style={{ marginBottom: '40px', padding: '24px', borderRadius: '20px', background: 'rgba(15, 23, 42, 0.6)', border: `1px solid ${portfolioData.summary.ai_insight.color}40`, position: 'relative', overflow: 'hidden' }}>
                                    <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: portfolioData.summary.ai_insight.color }} />

                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                                        <BrainCircuit style={{ color: portfolioData.summary.ai_insight.color, width: '24px' }} />
                                        <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 700 }}>Gestor de Fondos IA</h3>
                                        <div style={{ marginLeft: 'auto', background: `${portfolioData.summary.ai_insight.color}20`, color: portfolioData.summary.ai_insight.color, padding: '4px 12px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 800 }}>
                                            SCORE: {portfolioData.summary.ai_insight.score}/100
                                        </div>
                                    </div>

                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: portfolioData.summary.ai_insight.color, letterSpacing: '0.5px' }}>
                                            {portfolioData.summary.ai_insight.verdict}
                                        </div>
                                        <p style={{ margin: 0, fontSize: '1.05rem', color: '#cbd5e1', lineHeight: 1.6 }}>
                                            {portfolioData.summary.ai_insight.reason}
                                        </p>
                                    </div>
                                </div>
                            )}

                            <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '20px', color: '#94a3b8' }}>DESGLOSE TÉCNICO POR ACTIVO</h4>
                            <div className="asset-grid">
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
    );
};
