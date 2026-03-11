import React, { useMemo } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';

const VERDICT_COLORS = {
    1: '#10b981', // COMPRA (Incluye Fuerte Compra) - Green
    0: '#fbbf24', // MANTENER - Yellow
    2: '#ef4444'  // VENTA (Incluye Fuerte Venta) - Red
};

const CustomTooltip = ({ active, payload, currencySymbol }) => {
    if (active && payload && payload.length) {
        const item = payload.find(p => p.payload && p.payload.regime !== undefined) || payload[0];
        const data = item.payload;
        const isForecast = data.type === 'forecast';

        const getVerdictLabel = (id) => {
            const labels = {
                1: "Compra",
                0: "Mantener",
                2: "Venta"
            };
            return labels[id] || "Mantener";
        };

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
                {data.rvol != null && !isNaN(data.rvol) && (
                    <p style={{ margin: '4px 0 0', fontSize: '11px', color: data.rvol > 1.5 ? '#10b981' : data.rvol < 0.7 ? '#f87171' : '#94a3b8' }}>
                        Volumen: {data.rvol.toFixed(2)}x {data.rvol > 1.5 ? '(Alto)' : data.rvol < 0.7 ? '(Bajo)' : ''}
                    </p>
                )}
                {data.regime !== undefined && (
                    <p style={{ margin: '4px 0 0', fontSize: '11px', color: VERDICT_COLORS[Number(data.regime)] || '#94a3b8', fontWeight: 600 }}>
                        Estrategia AI: {getVerdictLabel(Number(data.regime))}
                    </p>
                )}
            </div>
        );
    }
    return null;
};

export const StockChart = ({ data, currencySymbol, loading }) => {
    const historyData = useMemo(() => data.filter(d => d.type !== 'forecast'), [data]);
    const totalPoints = historyData.length;

    const stops = useMemo(() => {
        if (totalPoints === 0) return [];
        return historyData.map((d, i) => {
            const offset = (i / (totalPoints - 1)) * 100;
            const color = VERDICT_COLORS[Number(d.regime)] || VERDICT_COLORS[0];
            return <stop key={i} offset={`${offset}%`} stopColor={color} />;
        });
    }, [historyData, totalPoints]);

    return (
        <div style={{ width: '100%', position: 'relative' }}>
            {/* Only show blocking overlay if there is NO data yet (first load) */}
            {loading && data.length === 0 && (
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(2, 6, 23, 0.6)', borderRadius: '12px', zIndex: 10 }}>
                    <div style={{ width: '40px', height: '40px', border: '4px solid #38bdf8', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                </div>
            )}
            {/* Subtle indicator when refreshing with existing data */}
            {loading && data.length > 0 && (
                <div style={{ position: 'absolute', top: '8px', right: '8px', width: '10px', height: '10px', borderRadius: '50%', background: '#38bdf8', animation: 'spin 1s linear infinite', zIndex: 10, border: '2px solid #38bdf830' }} />
            )}


            {/* Price Chart */}
            <div style={{ height: '350px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} syncId="stockChart">
                        <defs>
                            <linearGradient id="multiColor" x1="0" y1="0" x2="1" y2="0">
                                {stops}
                            </linearGradient>
                            <linearGradient id="multiFill" x1="0" y1="0" x2="1" y2="0">
                                {stops.map((stop, idx) => React.cloneElement(stop, { key: `f-${idx}`, stopOpacity: 0.2 }))}
                            </linearGradient>
                            <linearGradient id="volFill" x1="0" y1="0" x2="1" y2="0">
                                {stops.map((stop, idx) => React.cloneElement(stop, { key: `v-${idx}`, stopOpacity: 0.6 }))}
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                        <XAxis dataKey="date" hide={true} />
                        <YAxis hide={true} domain={['auto', 'auto']} />
                        <Tooltip content={<CustomTooltip currencySymbol={currencySymbol} />} />

                        <Area type="monotone" dataKey="range" stroke="none" fill="#818cf8" fillOpacity={0.1} connectNulls={true} />

                        <Area
                            type="monotone"
                            dataKey="historyPrice"
                            stroke="url(#multiColor)"
                            strokeWidth={3}
                            fill="url(#multiFill)"
                            isAnimationActive={false}
                        />

                        <Area type="monotone" dataKey="forecastPrice" stroke="#818cf8" strokeWidth={3} strokeDasharray="5 5" fillOpacity={0.1} fill="#818cf8" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* RVOL Chart */}
            <div style={{ height: '140px', width: '100%', marginTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '16px' }}>
                <div style={{ position: 'absolute', left: '10px', bottom: '125px', fontSize: '10px', fontWeight: 900, color: '#e2e8f0', textTransform: 'uppercase', letterSpacing: '1px', background: 'rgba(15, 23, 42, 0.8)', padding: '2px 8px', borderRadius: '4px' }}>
                    Volumen Relativo (RVOL)
                </div>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} syncId="stockChart">
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.08)" />
                        <XAxis dataKey="date" stroke="rgba(255,255,255,0.4)" fontSize={10} />
                        <YAxis hide={true} domain={[0, 'auto']} />
                        <Tooltip content={<CustomTooltip currencySymbol={currencySymbol} />} cursor={{ stroke: 'rgba(255,255,255,0.2)', strokeWidth: 1 }} />

                        <Area
                            type="monotone"
                            dataKey="rvol"
                            stroke="url(#multiColor)"
                            strokeWidth={2}
                            fill="url(#volFill)"
                            isAnimationActive={false}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
