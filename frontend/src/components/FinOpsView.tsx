import React from 'react';
import { DollarSign, ShieldAlert, CheckCircle2, ArrowDownRight, Layers } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { useChatStore } from '../stores/useChatStore';

export const FinOpsView: React.FC = () => {
  const { totalQueries, estimatedSavingsUsd } = useChatStore();

  const activeQueries = Math.max(totalQueries, 1);
  const costActual = activeQueries * 0.0003;
  const costGpt4 = activeQueries * 0.015;
  const savings = Math.max(costGpt4 - costActual, 0);
  const savingsPercent = ((savings / costGpt4) * 100).toFixed(1);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* FinOps Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">
            Auditoria Financeira & Governança FinOps
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Demonstrativo de eficiência de custo por requisição com roteamento agnóstico
          </p>
        </div>
        <Badge variant="success" className="text-xs font-semibold py-1 px-3">
          +{savingsPercent}% de Economia Efetiva
        </Badge>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-slate-200/90 shadow-xs">
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500">Custo Efetivo Médio</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">${costActual.toFixed(4)}</h3>
              <p className="text-[11px] text-blue-700 mt-1 font-medium">Gemini 3.8 / DeepSeek V4.1</p>
            </div>
            <div className="h-10 w-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
              <DollarSign className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs">
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500">Custo no GPT-4o Legado</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">${costGpt4.toFixed(4)}</h3>
              <p className="text-[11px] text-slate-500 mt-1">Benchmark Proprietário Monolítico</p>
            </div>
            <div className="h-10 w-10 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center">
              <ShieldAlert className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs">
          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500">Poupança Acumulada</p>
              <h3 className="text-2xl font-bold text-emerald-700 mt-1">
                ${(estimatedSavingsUsd > 0 ? estimatedSavingsUsd : savings).toFixed(4)}
              </h3>
              <p className="text-[11px] text-emerald-700 mt-1 flex items-center gap-1 font-medium">
                <ArrowDownRight className="h-3 w-3" /> Redução Direta em Produção
              </p>
            </div>
            <div className="h-10 w-10 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Model Tiering Table */}
      <Card className="border-slate-200/90 shadow-xs">
        <CardHeader>
          <CardTitle className="text-sm font-semibold text-slate-900 flex items-center gap-2">
            <Layers className="h-4 w-4 text-slate-500" />
            Matriz de Roteamento de Modelos por Complexidade Analítica
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full text-left text-xs border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-700 font-semibold">
                <tr>
                  <th className="p-3">Modelo</th>
                  <th className="p-3">Função na Arquitetura</th>
                  <th className="p-3">Entrada (/1M tokens)</th>
                  <th className="p-3">Saída (/1M tokens)</th>
                  <th className="p-3">Status de Cota</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700 bg-white">
                <tr className="hover:bg-slate-50">
                  <td className="p-3 font-semibold text-slate-900">Google Gemini 3.8 Flash</td>
                  <td className="p-3">Intent Router, NL2SQL & Síntese Rápida</td>
                  <td className="p-3 text-slate-900 font-medium">$0.075</td>
                  <td className="p-3 text-slate-900 font-medium">$0.30</td>
                  <td className="p-3"><Badge variant="success">Ativo (Gemini Pro)</Badge></td>
                </tr>
                <tr className="hover:bg-slate-50">
                  <td className="p-3 font-semibold text-slate-900">DeepSeek V4.1 Flash</td>
                  <td className="p-3">Fallback de Roteamento & Alto Volume</td>
                  <td className="p-3 text-slate-900 font-medium">$0.14</td>
                  <td className="p-3 text-slate-900 font-medium">$0.28</td>
                  <td className="p-3"><Badge variant="success">Ativo (26k req/5h)</Badge></td>
                </tr>
                <tr className="hover:bg-slate-50">
                  <td className="p-3 font-semibold text-slate-900">DeepSeek V4 Pro / Qwen3.8 Max</td>
                  <td className="p-3">Self-Healing em Queries Complexas</td>
                  <td className="p-3 text-slate-900 font-medium">$0.55</td>
                  <td className="p-3 text-slate-900 font-medium">$2.19</td>
                  <td className="p-3"><Badge variant="info">Ativo (OpenCode Go)</Badge></td>
                </tr>
                <tr className="hover:bg-slate-50 text-slate-400 bg-slate-50/50">
                  <td className="p-3 font-medium">GPT-4o (Linha de Base)</td>
                  <td className="p-3">Benchmark Comparativo</td>
                  <td className="p-3 text-red-600 font-medium">$2.50</td>
                  <td className="p-3 text-red-600 font-medium">$10.00</td>
                  <td className="p-3"><Badge variant="neutral">Evitado (+90% Custo)</Badge></td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
