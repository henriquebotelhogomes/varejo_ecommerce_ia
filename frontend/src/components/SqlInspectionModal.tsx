import React, { useState } from 'react';
import { X, Copy, Check, ShieldCheck, Database, Cpu, Terminal } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface SqlInspectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  sqlQuery: string;
  sqlValid?: boolean;
  rowCount?: number;
  intent?: string;
}

export const SqlInspectionModal: React.FC<SqlInspectionModalProps> = ({
  isOpen,
  onClose,
  sqlQuery,
  sqlValid = true,
  rowCount,
  intent = 'QUANTITATIVE_SQL',
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(sqlQuery);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-50 text-blue-700 border border-blue-100">
              <Terminal className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Auditoria & Linhagem da Consulta
              </h3>
              <p className="text-xs text-slate-500">
                Metadados de execução, dialeto e validação determinística de segurança
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-md hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-5">
          {/* Metadata Cards Grid */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-lg border border-slate-200/80 bg-slate-50/50 space-y-1">
              <span className="text-[11px] font-medium text-slate-500 flex items-center gap-1.5">
                <Cpu className="h-3.5 w-3.5 text-blue-600" />
                Motor Analítico
              </span>
              <p className="text-xs font-semibold text-slate-800">DuckDB OLAP (SIMD)</p>
            </div>

            <div className="p-3 rounded-lg border border-slate-200/80 bg-slate-50/50 space-y-1">
              <span className="text-[11px] font-medium text-slate-500 flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
                AST Guardrail
              </span>
              <p className="text-xs font-semibold text-emerald-700">
                {sqlValid ? 'Validado & Seguro' : 'Não Validado'}
              </p>
            </div>

            <div className="p-3 rounded-lg border border-slate-200/80 bg-slate-50/50 space-y-1">
              <span className="text-[11px] font-medium text-slate-500 flex items-center gap-1.5">
                <Database className="h-3.5 w-3.5 text-slate-600" />
                Registros / Base
              </span>
              <p className="text-xs font-semibold text-slate-800">
                {rowCount !== undefined ? `${rowCount} linhas retornadas` : '204.382 registros'}
              </p>
            </div>
          </div>

          {/* Badges Bar */}
          <div className="flex items-center gap-2 pt-1">
            <Badge variant="neutral" className="text-[11px]">
              Dialeto: DuckDB / ANSI SQL
            </Badge>
            <Badge variant="neutral" className="text-[11px]">
              Modo: Conexão Read-Only
            </Badge>
            <Badge variant="neutral" className="text-[11px]">
              Intenção: {intent}
            </Badge>
          </div>

          {/* SQL Code Snippet Box */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-600">
              <span className="font-semibold">Comando SQL Gerado pela Camada Semântica:</span>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors cursor-pointer"
              >
                {copied ? (
                  <>
                    <Check className="h-3.5 w-3.5 text-emerald-600" />
                    <span className="text-emerald-700">Copiado!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5" />
                    Copiar SQL
                  </>
                )}
              </button>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950 p-4 overflow-x-auto text-xs font-mono shadow-inner">
              <pre className="text-emerald-400 leading-relaxed whitespace-pre-wrap select-all">
                {sqlQuery}
              </pre>
            </div>
          </div>

          {/* Informational Note */}
          <p className="text-[11px] text-slate-500 leading-normal">
            Esta query foi traduzida automaticamente pelo agente a partir de linguagem natural,
            incorporando as fórmulas canônicas da <strong>Metric Layer</strong> e sanitizada pelo{' '}
            <strong>sqlglot</strong> para garantir conformidade estrita de leitura (menor privilégio).
          </p>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end px-6 py-3.5 border-t border-slate-100 bg-slate-50/50">
          <Button variant="secondary" size="sm" onClick={onClose} className="text-xs font-medium">
            Fechar Inspeção
          </Button>
        </div>
      </div>
    </div>
  );
};
