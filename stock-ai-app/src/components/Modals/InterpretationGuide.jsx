import React from 'react';
import { X, BookOpen } from 'lucide-react';

export const InterpretationGuide = ({ onClose }) => (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(2, 6, 23, 0.85)', backdropFilter: 'blur(8px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
        <div className="guide-modal" style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '24px', width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto', padding: '40px', position: 'relative' }}>
            <button onClick={onClose} style={{ position: 'absolute', right: '24px', top: '24px', background: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '50%', border: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8', cursor: 'pointer' }}>
                <X style={{ width: '24px', height: '24px' }} />
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '32px' }}>
                <BookOpen style={{ width: '32px', height: '32px', color: '#38bdf8' }} />
                <h2 style={{ fontSize: '2rem', fontWeight: 700, margin: 0 }}>Guía de Interpretación</h2>
            </div>

            <section style={{ marginBottom: '32px' }}>
                <h3 style={{ color: '#38bdf8', marginBottom: '16px', fontSize: '1.25rem' }}>1. El Sistema de Consenso (Triple Pilar) 🏛️</h3>
                <p style={{ color: '#94a3b8', lineHeight: 1.6 }}>La recomendación final ("COMPRA", "VENTA", etc.) es el resultado de una suma ponderada de tres modelos independientes. La puntuación va de 0 a 100.</p>

                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '16px', fontSize: '0.85rem', color: '#cbd5e1' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                            <th style={{ padding: '8px', textAlign: 'left', color: '#f8fafc' }}>Pilar</th>
                            <th style={{ padding: '8px', textAlign: 'left', color: '#f8fafc' }}>Peso</th>
                            <th style={{ padding: '8px', textAlign: 'left', color: '#f8fafc' }}>Qué Analiza</th>
                            <th style={{ padding: '8px', textAlign: 'left', color: '#f8fafc' }}>Métrica Clave</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                            <td style={{ padding: '8px' }}><strong>1. Estructura</strong></td>
                            <td style={{ padding: '8px' }}><strong>40%</strong></td>
                            <td style={{ padding: '8px' }}>Eficiencia del mercado actual</td>
                            <td style={{ padding: '8px' }}><strong>Ratio R/R</strong> (Rentabilidad/Riesgo) del Régimen HMM actual</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                            <td style={{ padding: '8px' }}><strong>2. Impulso</strong></td>
                            <td style={{ padding: '8px' }}><strong>30%</strong></td>
                            <td style={{ padding: '8px' }}>Aceleración del precio</td>
                            <td style={{ padding: '8px' }}><strong>Media</strong> del Régimen HMM de Diferencias</td>
                        </tr>
                        <tr>
                            <td style={{ padding: '8px' }}><strong>3. Proyección</strong></td>
                            <td style={{ padding: '8px' }}><strong>30%</strong></td>
                            <td style={{ padding: '8px' }}>Futuro probable (10 días)</td>
                            <td style={{ padding: '8px' }}><strong>Pendiente</strong> de la predicción del modelo Chronos (LLM)</td>
                        </tr>
                    </tbody>
                </table>

                {/* ... (Rest of content remains the same, omitted for brevity in this extraction tool call to avoid huge output, but in real file I'd paste it all. I will paste the full content for correctness) ... */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '24px' }}>
                    <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <h4 style={{ color: '#f8fafc', marginBottom: '8px' }}>A. Pilar Estructural (Max 40 pts)</h4>
                        <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 0 }}>Se basa en la calidad del estado actual de rendimientos:</p>
                        <ul style={{ fontSize: '0.8rem', color: '#94a3b8', paddingLeft: '16px', marginTop: '8px' }}>
                            <li><strong>100 pts</strong>: Ratio R/R &gt; 0.15 (Tendencia muy limpia)</li>
                            <li><strong>70 pts</strong>: Ratio R/R &gt; 0.05 (Tendencia positiva estándar)</li>
                            <li><strong>40 pts</strong>: Ratio R/R &gt;= 0 (Mercado lateral/ruido)</li>
                            <li><strong>10 pts</strong>: Ratio R/R &lt; 0 (Ineficiente/Riesgoso)</li>
                        </ul>
                    </div>
                    <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <h4 style={{ color: '#f8fafc', marginBottom: '8px' }}>B. Pilar de Impulso (Max 30 pts)</h4>
                        <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 0 }}>Mide la "fuerza G" del movimiento:</p>
                        <ul style={{ fontSize: '0.8rem', color: '#94a3b8', paddingLeft: '16px', marginTop: '8px' }}>
                            <li><strong>100 pts</strong>: Media &gt; 0.5 (Fuerte aceleración)</li>
                            <li><strong>75 pts</strong>: Media &gt; 0 (Aceleración moderada)</li>
                            <li><strong>30 pts</strong>: Media &gt; -0.5 (Desaceleración/Frenada)</li>
                            <li><strong>0 pts</strong>: Media &lt;= -0.5 (Caída libre)</li>
                        </ul>
                    </div>
                    <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                        <h4 style={{ color: '#f8fafc', marginBottom: '8px' }}>C. Pilar de Proyección (Max 30 pts)</h4>
                        <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: 0 }}>Mira hacia el futuro con IA Generativa:</p>
                        <ul style={{ fontSize: '0.8rem', color: '#94a3b8', paddingLeft: '16px', marginTop: '8px' }}>
                            <li><strong>100 pts</strong>: Tendencia &gt; +3% en 10 días</li>
                            <li><strong>70 pts</strong>: Tendencia &gt; 0%</li>
                            <li><strong>20 pts</strong>: Tendencia plana o ligeramente bajista</li>
                            <li><strong>0 pts</strong>: Tendencia &lt; -3% (Proyección de caída fuerte)</li>
                        </ul>
                    </div>
                </div>
            </section>

            <section style={{ marginBottom: '32px' }}>
                <h3 style={{ color: '#38bdf8', marginBottom: '16px', fontSize: '1.25rem' }}>2. Veredictos y Criterios 🎯</h3>
                <p style={{ color: '#94a3b8', lineHeight: 1.6 }}>La suma de los puntos anteriores genera el veredicto final:</p>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '16px', fontSize: '0.85rem', color: '#cbd5e1' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                <th style={{ padding: '8px', textAlign: 'left', color: '#f8fafc' }}>Puntuación Total</th>
                                <th style={{ padding: '8px', textAlign: 'left', color: '#f8fafc' }}>Veredicto</th>
                                <th style={{ padding: '8px', textAlign: 'left', color: '#f8fafc' }}>Significado</th>
                                <th style={{ padding: '8px', textAlign: 'left', color: '#f8fafc' }}>Estrategia Sugerida</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(16, 185, 129, 0.05)' }}>
                                <td style={{ padding: '8px' }}><strong>&gt;= 80</strong></td>
                                <td style={{ padding: '8px', color: '#34d399' }}><strong>🟢 COMPRA FUERTE</strong></td>
                                <td style={{ padding: '8px' }}>Estructura perfecta + Inercia + Futuro alcista.</td>
                                <td style={{ padding: '8px' }}><strong>Entrada agresiva</strong>. Ideal para aumentar posición.</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(250, 204, 21, 0.05)' }}>
                                <td style={{ padding: '8px' }}><strong>60 - 79</strong></td>
                                <td style={{ padding: '8px', color: '#facc15' }}><strong>🟡 COMPRA</strong></td>
                                <td style={{ padding: '8px' }}>Estructura positiva, pero falla algún pilar.</td>
                                <td style={{ padding: '8px' }}><strong>Entrada escalonada</strong>. Buscar confirmación.</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(248, 250, 252, 0.05)' }}>
                                <td style={{ padding: '8px' }}><strong>40 - 59</strong></td>
                                <td style={{ padding: '8px', color: '#cbd5e1' }}><strong>⚪ MANTENER</strong></td>
                                <td style={{ padding: '8px' }}>Zona de equilibrio. Fuerzas empatadas.</td>
                                <td style={{ padding: '8px' }}><strong>No operar</strong>. Mantener con Stop Loss.</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: 'rgba(251, 146, 60, 0.05)' }}>
                                <td style={{ padding: '8px' }}><strong>20 - 39</strong></td>
                                <td style={{ padding: '8px', color: '#fb923c' }}><strong>🟠 VENTA</strong></td>
                                <td style={{ padding: '8px' }}>Pérdida de eficiencia. Riesgo &gt; Beneficio.</td>
                                <td style={{ padding: '8px' }}><strong>Reducir riesgo</strong>. Cerrar parciales.</td>
                            </tr>
                            <tr style={{ background: 'rgba(239, 68, 68, 0.05)' }}>
                                <td style={{ padding: '8px' }}><strong>&lt; 20</strong></td>
                                <td style={{ padding: '8px', color: '#f87171' }}><strong>🔴 VENTA FUERTE</strong></td>
                                <td style={{ padding: '8px' }}>Colapso estructural y aceleración negativa.</td>
                                <td style={{ padding: '8px' }}><strong>Salida inmediata</strong>. No buscar suelo.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section style={{ marginBottom: '32px' }}>
                <h3 style={{ color: '#38bdf8', marginBottom: '16px', fontSize: '1.25rem' }}>3. Diccionario de Alertas de la IA 🔍</h3>
                <p style={{ color: '#94a3b8', lineHeight: 1.6 }}>Cuando el sistema detecta una anomalía, añade una nota entre paréntesis. Aquí explicamos qué significan y qué acción tomar:</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
                    {[
                        { tag: 'Riesgo Elevado (R/R neg)', desc: 'Estado destructivo. Volatilidad > Retorno.', action: 'Evitar nuevas entradas hasta que cambie el régimen.' },
                        { tag: 'Deceleración detectada', desc: 'Sube el precio pero baja la aceleración (Impulso). Signo de agotamiento.', action: 'Vigilar. No perseguir el precio. Riesgo de techo.' },
                        { tag: 'Proyección bajista', desc: 'La IA anticipa caída en 10 días pese a la subida actual.', action: 'Cautela. El modelo detecta patrones de distribución no visibles.' }
                    ].map((item, i) => (
                        <div key={i} style={{ padding: '16px', borderRadius: '16px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                <span style={{ color: '#fbbf24', fontWeight: 700, fontSize: '0.9rem' }}>{item.tag}</span>
                                <span style={{ color: '#10b981', fontSize: '0.75rem', fontWeight: 600 }}>{item.action}</span>
                            </div>
                            <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: 0 }}>{item.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section style={{ marginBottom: '32px' }}>
                <h3 style={{ color: '#38bdf8', marginBottom: '16px', fontSize: '1.25rem' }}>4. Consejos de Uso Práctico</h3>
                <ul style={{ color: '#94a3b8', fontSize: '0.9rem', paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <li><strong>Confirma la Inercia:</strong> Un "Impulso consolidado" (Estado HMM estable) es mucho más fiable que uno que cambia cada día.</li>
                    <li><strong>Mira las Probabilidades:</strong> Si el estado actual tiene una probabilidad cercana al <strong>90-100%</strong>, la señal es muy robusta. Si está cerca del 50-60%, el mercado está indeciso.</li>
                    <li><strong>Usa los dos HMM:</strong><br />
                        - <strong>HMM Rep (Retornos)</strong> te dice "Dónde estamos" (Alcista, Bajista, Lateral).<br />
                        - <strong>HMM Diff (Impulso)</strong> te dice "A qué velocidad vamos".<br />
                        <em>Ejemplo: Si HMM Rep es "Alcista" pero HMM Diff es "Volátil/Bajista", movimiento perdiendo gasolina.</em>
                    </li>
                </ul>
            </section>

            <section style={{ marginBottom: '32px' }}>
                <h3 style={{ color: '#38bdf8', marginBottom: '16px', fontSize: '1.25rem' }}>5. Índices Globales y Filtrado 🌍</h3>
                <p style={{ color: '#94a3b8', lineHeight: 1.6, marginBottom: '12px' }}>La nueva sección de <strong>Índices Globales</strong> permite analizar mercados completos (IBEX 35, DAX 40, NASDAQ 100, etc.) en busca de oportunidades.</p>
                <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(56, 189, 248, 0.05)', border: '1px solid rgba(56, 189, 248, 0.1)' }}>
                    <h4 style={{ color: '#f8fafc', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ background: '#38bdf8', color: '#0f172a', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>NUEVO</span>
                        Filtrado Inteligente "Solo Oportunidades"
                    </h4>
                    <p style={{ fontSize: '0.9rem', color: '#cbd5e1', margin: 0 }}>
                        Al seleccionar un índice, el sistema analiza <strong>todos</strong> sus componentes pero <strong>solo muestra</strong> aquellos con veredicto <strong>🟢 COMPRA FUERTE</strong>.
                    </p>
                    <ul style={{ fontSize: '0.85rem', color: '#94a3b8', paddingLeft: '20px', marginTop: '8px' }}>
                        <li>Esto elimina el ruido y te centra únicamente en los activos con la mejor estructura técnica y momento.</li>
                        <li>Si no se muestran resultados, significa que ningún activo del índice cumple los estrictos criterios de excelencia de la IA en este momento.</li>
                    </ul>
                </div>
            </section>
        </div>
    </div>
);
