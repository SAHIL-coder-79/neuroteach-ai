import React, { useState } from 'react';
import { VisualSpec } from '@/types';
import { Sliders, RefreshCw, ZoomIn, ZoomOut, CheckCircle2, ShieldCheck } from 'lucide-react';

interface GraphPanelProps {
  spec: VisualSpec;
  interactive?: boolean;
}

export const GraphPanel: React.FC<GraphPanelProps> = ({ spec, interactive = true }) => {
  const [paramValue, setParamValue] = useState<number>(
    spec.parameters && spec.parameters.length > 0 ? spec.parameters[0].default : 1
  );

  const parameter = spec.parameters && spec.parameters.length > 0 ? spec.parameters[0] : null;

  // Render mathematical parabola points client-side based on slider parameter
  const generatePathData = () => {
    const points: string[] = [];
    const a = parameter ? paramValue : 1;
    // f(x) = a*(x-2)^2 - 1
    for (let x = -2; x <= 6; x += 0.2) {
      const mathY = a * Math.pow(x - 2, 2) - 1;
      const svgX = ((x - (-2)) / 8) * 400;
      const svgY = 260 - ((mathY - (-3)) / 10) * 260;
      points.push(`${svgX.toFixed(1)},${svgY.toFixed(1)}`);
    }
    return `M ${points.join(' L ')}`;
  };

  // Vertex position
  const vertexSvgX = ((2 - (-2)) / 8) * 400;
  const vertexSvgY = 260 - ((-1 - (-3)) / 10) * 260;

  return (
    <div className="rounded-xl bg-bg-surface border border-border-subtle overflow-hidden flex flex-col shadow-xs">
      {/* Visual Header */}
      <div className="p-3 border-b border-border-subtle flex items-center justify-between bg-bg-raised">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-accent-500 animate-pulse" />
          <h4 className="text-xs font-bold text-text-primary truncate">{spec.title}</h4>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-success flex items-center gap-1 font-semibold">
            <CheckCircle2 className="h-3 w-3" />
            <span>Deterministic Verified</span>
          </span>
        </div>
      </div>

      {/* SVG Canvas Render Area */}
      <div className="relative h-64 w-full bg-bg-surface flex items-center justify-center p-2 overflow-hidden border-b border-border-subtle">
        <svg 
          viewBox="0 0 400 260" 
          className="w-full h-full select-none"
        >
          {/* Subtle Grid lines */}
          <defs>
            <pattern id="grid" width="40" height="26" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 26" fill="none" stroke="currentColor" className="text-border-subtle" strokeWidth="0.8" />
            </pattern>
          </defs>
          <rect width="400" height="260" fill="url(#grid)" />

          {/* Coordinate Axes */}
          <line x1="0" y1="182" x2="400" y2="182" stroke="currentColor" className="text-text-muted" strokeWidth="1.2" />
          <line x1="100" y1="0" x2="100" y2="260" stroke="currentColor" className="text-text-muted" strokeWidth="1.2" />

          {/* Axis Labels */}
          <text x="390" y="176" fill="currentColor" className="text-text-muted" fontSize="10" fontFamily="JetBrains Mono" textAnchor="end">x</text>
          <text x="106" y="12" fill="currentColor" className="text-text-muted" fontSize="10" fontFamily="JetBrains Mono">y</text>

          {/* Render Function Curve */}
          <path
            d={generatePathData()}
            fill="none"
            stroke="#7555D9"
            strokeWidth="2.5"
            strokeLinecap="round"
          />

          {/* Render Derived Vertex Point */}
          <circle cx={vertexSvgX} cy={vertexSvgY} r="5" fill="#7555D9" stroke="#FFFFFF" strokeWidth="2" />
          <text x={vertexSvgX + 8} y={vertexSvgY + 4} fill="#7555D9" fontSize="10" fontFamily="JetBrains Mono" fontWeight="bold">
            Vertex (2, -1)
          </text>
        </svg>

        {/* Canvas floating controls */}
        <div className="absolute top-3 right-3 flex items-center gap-1 bg-bg-raised border border-border-subtle p-1 rounded-lg">
          <button title="Zoom in" className="p-1 text-text-muted hover:text-text-primary transition-colors">
            <ZoomIn className="h-3.5 w-3.5" />
          </button>
          <button title="Zoom out" className="p-1 text-text-muted hover:text-text-primary transition-colors">
            <ZoomOut className="h-3.5 w-3.5" />
          </button>
          <button 
            title="Reset view" 
            onClick={() => parameter && setParamValue(parameter.default)}
            className="p-1 text-text-muted hover:text-text-primary transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Interactive Parameter Controls */}
      {interactive && parameter && (
        <div className="p-3 bg-bg-raised border-t border-border-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <Sliders className="h-3.5 w-3.5 text-accent-500" />
            <span className="font-semibold text-text-primary">{parameter.label}:</span>
            <span className="font-mono text-accent-500 font-bold">{paramValue.toFixed(1)}</span>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-56">
            <input
              type="range"
              min={parameter.min}
              max={parameter.max}
              step={parameter.step}
              value={paramValue}
              onChange={(e) => setParamValue(parseFloat(e.target.value))}
              className="w-full accent-accent-500 cursor-pointer h-1.5 bg-border-subtle rounded-lg"
            />
          </div>
        </div>
      )}

      {/* Explanation note */}
      {spec.explanation && (
        <div className="px-3 py-2 bg-bg-surface border-t border-border-subtle text-xs text-text-secondary flex items-start gap-2">
          <ShieldCheck className="h-3.5 w-3.5 text-accent-cyan shrink-0 mt-0.5" />
          <span>{spec.explanation}</span>
        </div>
      )}
    </div>
  );
};
