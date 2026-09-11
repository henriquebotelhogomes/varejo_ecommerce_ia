import React, { useEffect, useState } from 'react';
import { ShoppingCart, Activity, FileCode2, BarChart3, MessageSquare, DollarSign } from 'lucide-react';
import { Badge } from './ui/badge';
import { useChatStore } from '../stores/useChatStore';
import { fetchHealth } from '../services/api';

export const Header: React.FC = () => {
  const { activeTab, setActiveTab } = useChatStore();
  const [isHealthy, setIsHealthy] = useState<boolean>(true);

  useEffect(() => {
    fetchHealth()
      .then((res) => setIsHealthy(res.database_ready))
      .catch(() => setIsHealthy(false));
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-sm px-6 py-3.5 shadow-xs">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Logo & Product Title */}
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-slate-900 flex items-center justify-center text-white shadow-xs">
            <ShoppingCart className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold text-slate-900 tracking-tight">
                RetailSense
              </span>
              <span className="text-xs font-semibold text-slate-400">|</span>
              <span className="text-xs font-medium text-slate-600">
                Analytics & Customer Experience
              </span>
              <Badge variant={isHealthy ? 'success' : 'warning'}>
                <Activity className="h-3 w-3" />
                {isHealthy ? 'Catálogo Conectado (204k)' : 'Verificando Base'}
              </Badge>
            </div>
            <p className="text-[11px] text-slate-500">
              Métricas Consolidadas de Varejo • Motor Colunar DuckDB OLAP (SIMD) & Parquet
            </p>
          </div>
        </div>

        {/* Tab Navigation - Clean Segmented Control */}
        <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'dashboard'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200/60 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            <BarChart3 className="h-3.5 w-3.5" />
            Visão Geral
          </button>
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'chat'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200/60 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            <MessageSquare className="h-3.5 w-3.5" />
            Explorador de Dados
          </button>
          <button
            onClick={() => setActiveTab('finops')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === 'finops'
                ? 'bg-white text-slate-900 shadow-xs border border-slate-200/60 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            <DollarSign className="h-3.5 w-3.5" />
            Auditoria de Custos
          </button>
          <a
            href="/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium text-slate-600 hover:text-blue-600 hover:bg-slate-200/50 transition-all border-l border-slate-200 ml-1 cursor-pointer"
          >
            <FileCode2 className="h-3.5 w-3.5 text-blue-600" />
            Scalar Docs
          </a>
        </nav>
      </div>
    </header>
  );
};
