import React from 'react';
import { getRegime, getCurrencySymbol } from '../../utils/formatters';

export const AssetCard = ({ asset }) => {
    return (
        <div style={{ padding: '20px', borderRadius: '18px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                    <div style={{ fontWeight: 900, fontSize: '1.2rem' }}>{asset.ticker}</div>
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{getCurrencySymbol(asset.currency)}{asset.current_price.toFixed(2)}</div>
                </div>
                <div style={{ padding: '4px 10px', borderRadius: '6px', background: asset.recommendation.color + '20', color: asset.recommendation.color, fontSize: '0.7rem', fontWeight: 800 }}>
                    {asset.recommendation.verdict}
                </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '6px 10px', borderRadius: '8px', background: getRegime(asset.current_regime_ret).color + '15', border: `1px solid ${getRegime(asset.current_regime_ret).color}30` }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: getRegime(asset.current_regime_ret).color }}>
                        HMM: {getRegime(asset.current_regime_ret).label}
                    </span>
                    <span style={{ fontSize: '0.65rem', color: '#94a3b8' }}>
                        μ: {(asset.state_stats_ret?.find(s => s.regime === asset.current_regime_ret)?.mean || 0).toFixed(3)}%
                    </span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '6px 10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#cbd5e1' }}>
                        IMP: {getRegime(asset.current_regime_diff).label}
                    </span>
                    <span style={{ fontSize: '0.65rem', color: '#94a3b8' }}>
                        μ: {(asset.state_stats_diff?.find(s => s.regime === asset.current_regime_diff)?.mean || 0).toFixed(3)}%
                    </span>
                </div>
            </div>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5, minHeight: '4.5em', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                {asset.recommendation.reason}
            </p>
        </div>
    );
};
