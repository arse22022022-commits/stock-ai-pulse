import React from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import { getRegime } from '../../utils/formatters';

const CustomTooltip = ({ active, payload, currencySymbol }) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        const isForecast = data.type === 'forecast';
        const regime = getRegime(data.regime);
        return (
            <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', padding: '12px', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.4)' }}>
                <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>{data.date}</p>
                <p style={{ margin: '4px 0 0', fontSize: '16px', fontWeight: 700, color: isForecast ? '#818cf8' : '#38bdf8' }}>
                    {currencySymbol}{data.price ? data.price.toFixed(2) : '0.00'}
                    {isForecast && <span style={{ fontSize: '10px', marginLeft: '6px', opacity: 0.8 }}>(Forecast)</span>}
                </p>
                {isForecast && data.price_low && data.price_high && (
                    <p style={{ margin: '4px 0 0', fontSize: '11px', color: '#94a3b8' }}>
                        Rango: {currencySymbol}{data.price_low.toFixed(2)} - {currencySymbol}{data.price_high.toFixed(2)}
                    </p>
                )}
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

export const StockChart = ({ data, currencySymbol, loading }) => {
    return (
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
                    <Tooltip content={<CustomTooltip currencySymbol={currencySymbol} />} />
                    {/* Shadow band for forecast range */}
                    <Area type="monotone" dataKey="range" stroke="none" fill="#818cf8" fillOpacity={0.3} connectNulls={true} />
                    <Area type="monotone" dataKey="historyPrice" stroke="#38bdf8" strokeWidth={3} fillOpacity={0.1} fill="#38bdf8" />
                    <Area type="monotone" dataKey="forecastPrice" stroke="#818cf8" strokeWidth={3} strokeDasharray="5 5" fillOpacity={0.1} fill="#818cf8" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};
