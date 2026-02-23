import React from 'react';
import { AlertTriangle } from 'lucide-react';

export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("ErrorBoundary atrapó un crash de React:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: '24px', background: '#ef444420', border: '1px solid #ef4444', borderRadius: '16px', color: '#f8fafc', margin: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px', color: '#ef4444' }}>
                        <AlertTriangle />
                        <h3 style={{ margin: 0 }}>Error de Renderizado (Mitigado)</h3>
                    </div>
                    <p style={{ color: '#cbd5e1' }}>La interfaz ha encontrado un cruce de datos incompatible o un valor nulo inesperado desde el servidor. El sistema ha blindado la caída para mantener la aplicación abierta.</p>
                    <pre style={{ background: 'rgba(0,0,0,0.5)', padding: '12px', borderRadius: '8px', overflowX: 'auto', fontSize: '0.8rem', color: '#fca5a5', whiteSpace: 'pre-wrap' }}>
                        {this.state.error && this.state.error.toString()}
                    </pre>
                    <button
                        onClick={() => window.location.reload()}
                        style={{ marginTop: '16px', padding: '10px 20px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}
                    >
                        Pulsar para Reiniciar Interfaz
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}
