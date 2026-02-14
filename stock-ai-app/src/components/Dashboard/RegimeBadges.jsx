import React from 'react';
import { Zap, BarChart3 } from 'lucide-react';
import { REGIME_INFO } from '../../utils/formatters';

export const RegimeBadges = ({
    currentRegime,
    currentRegimeDiff,
    probsRet,
    probsDiff,
    stateStatsRet,
    stateStatsDiff
}) => {
    return (
        <div className="side-panels" style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column', gap: '20px' }}>
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
                                <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: '#94a3b8' }}>
                                    <span>μ: {(stats.mean || 0).toFixed(3)}%</span>
                                    <span>σ: {(stats.std || 0).toFixed(3)}%</span>
                                    <span style={{ color: (stats.ratio_rr > 0) ? '#34d399' : '#f87171' }}>R/R: {(stats.ratio_rr || 0).toFixed(2)}</span>
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
                                <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: '#94a3b8' }}>
                                    <span style={{ color: (stats.mean > 0) ? '#38bdf8' : '#f87171' }}>Impulso (μ): {(stats.mean || 0).toFixed(3)}%</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};
