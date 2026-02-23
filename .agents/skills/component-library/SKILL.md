---
name: component-library
description: Estilo principal, reglas CSS y convenciones frontend para crear nuevos componentes React
---

# Librería de UI y Componentes

Esta skill encapsula el "Look & Feel" y el paradigma de programación utilizado para el Dashboard de **StockAI Pulse**. Cualquier interfaz futura debe regirse íntegramente por estas leyes visuales.

## Paleta de Colores (Theme)
- **Fondo Global (Background):** `#0f172a` (Slate-900).
- **Acentos y Botones Activos (Primary):** `#38bdf8` (Neon Blue/Sky Blue).
- **Tarjetas Traslúcidas:** Fondos basados en RGBA semitransparente: `background: rgba(255, 255, 255, 0.05)` a `0.1` combinado con filtro `backdrop-filter: blur(8px)`.
- **Bordes Contenedores:** Delgados y suaves. `1px solid rgba(255, 255, 255, 0.1)`.
- **Textos:**
    - Títulos y cuerpo destacado: `#f8fafc` (blanco con tono frío).
    - Títulos secundarios y ayudas de lectura: `#94a3b8`.
    - Semántica Peligro: `#f87171` / Éxito: `#34d399` / Atención: `#fbbf24`.

## Convenciones de Desarrollo Frontend

1. **Framework y Librerías**:
    - Utiliza componentes JSX estandarizados (React).
    - Evita arquitecturas pesadas o stores globales (`Redux`). Manten la gestión de estado controlada mediante Props Contexts localizados cuando proceda y Hooks nativos (`useState`, `useEffect`).
    - Para tipografía de iconos y widgets inyecta la librería `lucide-react`.
    - Animaciones simples con `transition: ...` de CSS y keyframes genéricos en `<style>` tags integradas al componente. No incluyas Framer-Motion u otras hiper dependencias.

2. **Diseño Responsivo Obligatorio**:
    - Cualquier vista de Grid debe contemplar el viewport condicionado. Utiliza `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))` para contenedores fluidos que se adaptan naturalmente a móviles y PC.
    - Padding relativo y márgenes calculados previstos en porcentajes o uniones VW-VH cuando el elemento sature la pantalla.

3. **Arquitectura Modulada por Vista**:
    - No acumules componentes heterogéneos en el `App.jsx`.
    - Instancia las pantallas gigantes en carpetas en `src/components/...` (ej. `PortfolioView.jsx` o `IndicesView.jsx`) y exporta como _defaults_ o constantes importables limpiamente.
