import React from 'react';
import { StockChart } from './StockChart';
import { RegimeBadges } from './RegimeBadges';
import { getRegime, getCurrencySymbol } from '../../utils/formatters';

export const StockDashboard = ({ ticker, metrics, data, loading }) => {
    const currencySymbol = getCurrencySymbol(metrics.currency);
    const regRet = getRegime(metrics.currentRegime);
    const regDiff = getRegime(metrics.currentRegimeDiff);
    const recommendation = metrics.recommendation;

    return (
        <div className="main-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '24px' }}>
            {/* Market Status Overview */}
            <div className="chart-panel" style={{ gridColumn: 'span 8', padding: '24px', borderRadius: '24px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                    <div>
                        <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '4px' }}>Precio en vivo ({ticker})</p>
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px' }}>
                            <h2 style={{ fontSize: '2.5rem', fontWeight: 700, margin: 0 }}>
                                {currencySymbol}{metrics.price ? metrics.price.toFixed(2) : '0.00'}
                            </h2>
                            <span style={{ color: (metrics.changePct || 0) >= 0 ? '#10b981' : '#ef4444', fontWeight: 600 }}>
                                {(metrics.changePct || 0) >= 0 ? '+' : ''}{(metrics.changePct || 0).toFixed(2)}%
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
                        {metrics.stateStatsRet.length > 0 && (
                            <span style={{ padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 600, backgroundColor: 'rgba(56, 189, 248, 0.1)', color: '#38bdf8', border: '1px solid rgba(56, 189, 248, 0.4)' }}>
                                R/R Actual: {(metrics.stateStatsRet.find(s => s.regime === metrics.currentRegime)?.ratio_rr || 0).toFixed(2)}
                            </span>
                        )}
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

                <StockChart data={data} currencySymbol={currencySymbol} loading={loading} />
            </div>

            <RegimeBadges
                currentRegime={metrics.currentRegime}
                currentRegimeDiff={metrics.currentRegimeDiff}
                probsRet={metrics.probsRet}
                probsDiff={metrics.probsDiff}
                stateStatsRet={metrics.stateStatsRet}
                stateStatsDiff={metrics.stateStatsDiff}
            />
        </div>
    );
};
