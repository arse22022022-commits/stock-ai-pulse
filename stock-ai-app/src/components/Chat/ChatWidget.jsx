import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2, Sparkles } from 'lucide-react';

export const ChatWidget = ({ context }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'assistant', content: '¿Hola! Soy tu asistente financiero. ¿Tienes dudas sobre este análisis?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const API_URL = import.meta.env.PROD ? '' : (import.meta.env.VITE_API_URL || 'http://localhost:8001');

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);

        try {
            const response = await fetch(`${API_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ticker: context.ticker,
                    price: context.price,
                    hmm_state: context.hmm_state,
                    impulse_state: context.impulse_state,
                    user_query: userMsg
                })
            });

            const data = await response.json();

            if (!response.ok) throw new Error(data.detail || 'Error en la respuesta');

            setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        } catch (error) {
            console.error('Chat Error:', error);
            setMessages(prev => [...prev, { role: 'assistant', content: '⚠️ Lo siento, tuve un problema al conectar con el cerebro de la IA. Inténtalo de nuevo.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                style={{
                    position: 'fixed',
                    bottom: '24px',
                    right: '24px',
                    width: '60px',
                    height: '60px',
                    borderRadius: '30px',
                    backgroundColor: '#38bdf8',
                    color: '#0f172a',
                    border: 'none',
                    boxShadow: '0 4px 12px rgba(56, 189, 248, 0.4)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 50,
                    transition: 'transform 0.2s'
                }}
                onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.1)'}
                onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
            >
                <MessageCircle size={32} />
            </button>
        );
    }

    return (
        <div style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            width: '450px',
            height: '650px',
            maxHeight: '85vh',
            backgroundColor: '#0f172a',
            borderRadius: '16px',
            border: '1px solid rgba(56, 189, 248, 0.2)',
            boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 50,
            overflow: 'hidden'
        }}>
            {/* Header */}
            <div style={{
                padding: '16px',
                background: 'linear-gradient(90deg, rgba(56, 189, 248, 0.1), transparent)',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Sparkles size={20} color="#38bdf8" />
                    <span style={{ fontWeight: 700, color: '#f8fafc' }}>AI Analyst</span>
                    <span style={{ fontSize: '0.75rem', background: '#334155', padding: '2px 6px', borderRadius: '4px', color: '#94a3b8' }}>
                        {context.ticker}
                    </span>
                </div>
                <button
                    onClick={() => setIsOpen(false)}
                    style={{
                        background: 'rgba(255,255,255,0.05)',
                        border: 'none',
                        color: '#f8fafc', // High contrast
                        cursor: 'pointer',
                        padding: '8px',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        transition: 'background 0.2s'
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.15)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                >
                    <X size={20} />
                </button>
            </div>

            {/* Messages */}
            <div style={{
                flex: 1,
                padding: '16px',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
            }}>
                {messages.map((msg, idx) => (
                    <div key={idx} style={{
                        alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '85%',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        background: msg.role === 'user' ? '#38bdf8' : 'rgba(255,255,255,0.05)',
                        color: msg.role === 'user' ? '#0f172a' : '#e2e8f0',
                        fontSize: '0.95rem',
                        lineHeight: 1.6,
                        borderBottomRightRadius: msg.role === 'user' ? '2px' : '12px',
                        borderBottomLeftRadius: msg.role === 'assistant' ? '2px' : '12px'
                    }}>
                        {msg.content}
                    </div>
                ))}

                {isLoading && (
                    <div style={{
                        alignSelf: 'flex-start',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        background: 'rgba(255,255,255,0.05)',
                        color: '#94a3b8',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '0.85rem'
                    }}>
                        <Loader2 className="spin" size={16} />
                        <span>Analizando mercado...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div style={{
                padding: '16px',
                borderTop: '1px solid rgba(255,255,255,0.05)',
                background: '#020617'
            }}>
                <div style={{
                    display: 'flex',
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: '24px',
                    padding: '4px 4px 4px 16px',
                    alignItems: 'center'
                }}>
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Pregunta sobre el análisis..."
                        style={{
                            flex: 1,
                            background: 'transparent',
                            border: 'none',
                            color: '#f8fafc',
                            outline: 'none',
                            fontSize: '0.9rem'
                        }}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isLoading}
                        style={{
                            width: '36px',
                            height: '36px',
                            borderRadius: '18px',
                            background: input.trim() ? '#38bdf8' : 'transparent',
                            border: 'none',
                            color: input.trim() ? '#0f172a' : '#475569',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: input.trim() ? 'pointer' : 'default',
                            transition: 'all 0.2s'
                        }}
                    >
                        <Send size={18} />
                    </button>
                </div>
                <div style={{ textAlign: 'center', marginTop: '8px' }}>
                    <span style={{ fontSize: '0.7rem', color: '#475569' }}>
                        Powered by Google Gemini
                    </span>
                </div>
            </div>

            <style>{`
                .spin { animation: spin 1s linear infinite; }
                @keyframes spin { 100% { transform: rotate(360deg); } }
            `}</style>
        </div>
    );
};
