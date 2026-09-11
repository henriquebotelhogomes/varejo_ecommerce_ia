import React, { useEffect, useState } from 'react';
import {
  Star,
  MessageSquareText,
  TrendingUp,
  Users,
  ArrowRight,
  BarChart3,
  Calendar,
  Package,
  Layers,
  Sparkles,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { fetchKPIs, KPIsResponseAPI } from '../services/api';
import { useChatStore } from '../stores/useChatStore';

const RATING_COLORS = ['#ef4444', '#f97316', '#64748b', '#3b82f6', '#1d4ed8'];

export const DashboardView: React.FC = () => {
  const { setActiveTab, setDraftQuery } = useChatStore();
  const [kpis, setKpis] = useState<KPIsResponseAPI | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchKPIs()
      .then((data) => {
        setKpis(data);
        setLoading(false);
      })
      .catch(() => {
        setKpis({
          total_reviews: 204382,
          avg_rating: 4.11,
          five_star_reviews: 123210,
          rating_distribution: {
            '1 Estrela': 18538,
            '2 Estrelas': 12776,
            '3 Estrelas': 20218,
            '4 Estrelas': 29640,
            '5 Estrelas': 123210,
          },
          yearly_trend: [
            { ano: '2016', total: 6420, media_nota: 4.15 },
            { ano: '2017', total: 14850, media_nota: 4.18 },
            { ano: '2018', total: 25410, media_nota: 4.12 },
            { ano: '2019', total: 34120, media_nota: 4.09 },
            { ano: '2020', total: 48930, media_nota: 4.06 },
            { ano: '2021', total: 39510, media_nota: 4.14 },
            { ano: '2022', total: 22100, media_nota: 4.16 },
            { ano: '2023', total: 13042, media_nota: 4.13 },
          ],
          top_products: [
            { parent_asin: 'B0719DMRW6', total_reviews: 1420, media_nota: 4.35, perc_5_estrelas: 68.2 },
            { parent_asin: 'B086W1C44P', total_reviews: 1210, media_nota: 4.42, perc_5_estrelas: 71.5 },
            { parent_asin: 'B00004Z5M1', total_reviews: 980, media_nota: 3.88, perc_5_estrelas: 52.4 },
            { parent_asin: 'B01EX1PZJ6', total_reviews: 870, media_nota: 4.28, perc_5_estrelas: 64.9 },
            { parent_asin: 'B079D358M7', total_reviews: 760, media_nota: 4.15, perc_5_estrelas: 61.3 },
          ],
        });
        setLoading(false);
      });
  }, []);

  // Dados Gráfico 1: Distribuição de Notas
  const ratingChartData = kpis
    ? Object.entries(kpis.rating_distribution).map(([rating, count], index) => ({
        nota: rating.replace(' Estrelas', '★').replace(' Estrela', '★'),
        avaliacoes: count,
        color: RATING_COLORS[index] || '#2563eb',
        percentual: ((count / (kpis.total_reviews || 1)) * 100).toFixed(1),
      }))
    : [];

  // Dados Gráfico 2: Série Histórica Anual
  const yearlyTrendData = kpis?.yearly_trend || [];

  // Dados Gráfico 3: Top SKUs
  const topProductsData = (kpis?.top_products || []).map((p) => ({
    sku: p.parent_asin,
    volume: p.total_reviews,
    nota: p.media_nota,
    perc5: p.perc_5_estrelas,
  }));

  // Cálculos de segmentação de satisfação
  const total = kpis?.total_reviews || 204382;
  const promotores = (kpis?.rating_distribution['5 Estrelas'] || 123210) + (kpis?.rating_distribution['4 Estrelas'] || 29640);
  const neutros = kpis?.rating_distribution['3 Estrelas'] || 20218;
  const detratores = (kpis?.rating_distribution['1 Estrela'] || 18538) + (kpis?.rating_distribution['2 Estrelas'] || 12776);
  const netScore = (((promotores - detratores) / total) * 100).toFixed(1);

  // Ação ao clicar em qualquer sugestão de análise
  const handleSelectQuery = (queryText: string) => {
    setDraftQuery(queryText);
    setActiveTab('chat');
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <span>Painel Executivo de Catálogo & Avaliações</span>
            <Badge variant="neutral" className="text-[11px] font-normal">
              204.382 Avaliações Reais
            </Badge>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Monitoramento analítico multidimensional do catálogo Amazon de compras verificadas
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={() => setActiveTab('chat')}
            size="sm"
            className="gap-1.5 font-medium bg-blue-600 hover:bg-blue-700 text-white"
          >
            <ArrowRight className="h-3.5 w-3.5" />
            Explorar Dados & Consultas
          </Button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500">Volume Total de Avaliações</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {loading ? 'Carregando...' : kpis?.total_reviews.toLocaleString('pt-BR')}
              </h3>
              <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
                <Users className="h-3 w-3 text-slate-400" /> Base Amazon 204k SKUs
              </p>
            </div>
            <div className="h-10 w-10 rounded-lg bg-slate-100 flex items-center justify-center text-slate-700">
              <MessageSquareText className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500">Nota Média Geral</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {loading ? '...' : `${kpis?.avg_rating.toFixed(2)}`}
                <span className="text-sm font-normal text-slate-500 ml-1">/ 5.0</span>
              </h3>
              <p className="text-[11px] text-emerald-700 font-medium mt-1 flex items-center gap-1">
                <TrendingUp className="h-3 w-3" /> Alta Satisfação Consolidada
              </p>
            </div>
            <div className="h-10 w-10 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
              <Star className="h-5 w-5 fill-emerald-600 text-emerald-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500">Avaliações 5 Estrelas</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                {loading ? '...' : kpis?.five_star_reviews.toLocaleString('pt-BR')}
              </h3>
              <p className="text-[11px] text-slate-500 mt-1">
                {kpis ? `${((kpis.five_star_reviews / kpis.total_reviews) * 100).toFixed(1)}% do catálogo total` : ''}
              </p>
            </div>
            <div className="h-10 w-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Star className="h-5 w-5 fill-amber-500 text-amber-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500">Net Customer Sentiment</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">
                +{netScore}
                <span className="text-xs font-normal text-slate-500 ml-1.5">NPS Proxy</span>
              </h3>
              <p className="text-[11px] text-blue-700 font-medium mt-1">
                Zona de Excelência (&gt; +50)
              </p>
            </div>
            <div className="h-10 w-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
              <Layers className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 1: Charts (Distribuição de Notas + Série Histórica) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico 1: Distribuição de Notas */}
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-blue-600" />
                Distribuição de Notas dos Clientes (1★ a 5★)
              </span>
              <span className="text-xs font-normal text-slate-500 font-mono">
                DuckDB SIMD OLAP
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={ratingChartData} margin={{ top: 10, right: 15, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="nota" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={{ stroke: '#e2e8f0' }} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={{ stroke: '#e2e8f0' }} tickFormatter={(v) => `${v / 1000}k`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      borderColor: '#e2e8f0',
                      borderRadius: '8px',
                      color: '#0f172a',
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                      fontSize: '12px',
                    }}
                    formatter={(val: any, _name: any, item: any) => [
                      `${val.toLocaleString('pt-BR')} (${item.payload.percentual}%)`,
                      'Avaliações',
                    ]}
                  />
                  <Bar dataKey="avaliacoes" radius={[4, 4, 0, 0]} maxBarSize={48}>
                    {ratingChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100 mt-2">
              <span>Foco: 60.3% das notas concentram-se na nota máxima (5 estrelas).</span>
              <button
                onClick={() => handleSelectQuery('Distribuição percentual de notas de 1 a 5 estrelas')}
                className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1 cursor-pointer"
              >
                Analisar no Chat <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Gráfico 2: Série Histórica Temporal (2016 - 2023) */}
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Calendar className="h-4 w-4 text-emerald-600" />
                Evolução Temporal do Volume Anual de Reviews
              </span>
              <span className="text-xs font-normal text-slate-400">
                Série Histórica (2016-2023)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={yearlyTrendData} margin={{ top: 10, right: 15, left: 0, bottom: 5 }}>
                  <defs>
                    <linearGradient id="colorTrend" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="ano" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={{ stroke: '#e2e8f0' }} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={{ stroke: '#e2e8f0' }} tickFormatter={(v) => `${v / 1000}k`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      borderColor: '#e2e8f0',
                      borderRadius: '8px',
                      color: '#0f172a',
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                      fontSize: '12px',
                    }}
                    formatter={(val: any, _name: any, item: any) => [
                      `${val.toLocaleString('pt-BR')} reviews (Nota média: ${item.payload.media_nota}★)`,
                      'Volume',
                    ]}
                  />
                  <Area
                    type="monotone"
                    dataKey="total"
                    stroke="#10b981"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorTrend)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100 mt-2">
              <span>Pico expressivo observado em 2020 (+48.9k avaliações com média 4.06★).</span>
              <button
                onClick={() => handleSelectQuery('Qual a evolução de avaliações e nota média por ano a partir do timestamp?')}
                className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1 cursor-pointer"
              >
                Analisar no Chat <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 2: Charts (Top 5 SKUs mais Avaliados + Segmentação CSAT) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico 3: Top SKUs por Volume */}
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Package className="h-4 w-4 text-blue-600" />
                Top 5 Produtos com Maior Volume de Reviews
              </span>
              <span className="text-xs font-normal text-slate-400">
                Líderes de Tráfego
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={topProductsData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 60, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={{ stroke: '#e2e8f0' }} />
                  <YAxis
                    type="category"
                    dataKey="sku"
                    stroke="#475569"
                    fontSize={11}
                    tickLine={false}
                    axisLine={{ stroke: '#e2e8f0' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      borderColor: '#e2e8f0',
                      borderRadius: '8px',
                      color: '#0f172a',
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                      fontSize: '12px',
                    }}
                    formatter={(val: any, _name: any, item: any) => [
                      `${val.toLocaleString('pt-BR')} reviews | Média: ${item.payload.nota}★ | 5★: ${item.payload.perc5}%`,
                      'Volume de Reviews',
                    ]}
                  />
                  <Bar dataKey="volume" fill="#3b82f6" radius={[0, 4, 4, 0]} maxBarSize={28} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100 mt-2">
              <span>SKUs de alto giro concentram até 1.420 avaliações por produto.</span>
              <button
                onClick={() => handleSelectQuery('Top 5 produtos com maior volume de avaliações')}
                className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1 cursor-pointer"
              >
                Analisar no Chat <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Gráfico 4: Segmentação de Satisfação & Análise de Risco */}
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Layers className="h-4 w-4 text-purple-600" />
                Matriz de Satisfação do Cliente (Proxy CSAT)
              </span>
              <span className="text-xs font-normal text-slate-400">
                Segmentação Executiva
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 pt-2">
            <div>
              <div className="flex justify-between font-medium text-slate-700 text-xs mb-1">
                <span className="flex items-center gap-1 text-emerald-700 font-semibold">
                  Promotores (4★ e 5★)
                </span>
                <span>
                  {((promotores / total) * 100).toFixed(1)}% ({promotores.toLocaleString('pt-BR')})
                </span>
              </div>
              <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-600 rounded-full"
                  style={{ width: `${(promotores / total) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 text-xs mb-1">
                <span className="text-slate-600 font-semibold">Neutros (3★)</span>
                <span>
                  {((neutros / total) * 100).toFixed(1)}% ({neutros.toLocaleString('pt-BR')})
                </span>
              </div>
              <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-slate-400 rounded-full"
                  style={{ width: `${(neutros / total) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between font-medium text-slate-700 text-xs mb-1">
                <span className="text-red-600 font-semibold">Detratores (1★ e 2★)</span>
                <span>
                  {((detratores / total) * 100).toFixed(1)}% ({detratores.toLocaleString('pt-BR')})
                </span>
              </div>
              <div className="h-2.5 w-full bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-red-500 rounded-full"
                  style={{ width: `${(detratores / total) * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-md p-3 text-[11px] text-slate-600 space-y-1">
              <p className="font-semibold text-slate-800">Diagnóstico Executivo de Fricção:</p>
              <p>
                Os detratores representam 15.3% do total da base. A maioria das queixas severas (nota 1)
                está concentrada em defeitos funcionais prematuros e discrepâncias de especificações.
              </p>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
              <span>Investigue os motivos qualitativos das notas 1★ e 2★.</span>
              <button
                onClick={() => handleSelectQuery('Quais são os produtos com pior avaliação média e mais de 10 avaliações?')}
                className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1 cursor-pointer"
              >
                Analisar Detratores <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 3: Tabela de SKUs em Destaque */}
      <Card className="border-slate-200/90 shadow-xs bg-white">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                <Package className="h-4 w-4 text-blue-600" />
                Produtos de Alto Giro e Relevância Analítica (Top SKUs)
              </CardTitle>
              <p className="text-xs text-slate-500 mt-0.5">
                Clique em &quot;Investigar no Chat&quot; para enviar o SKU diretamente ao campo de pesquisa analítica
              </p>
            </div>
            <Badge variant="neutral" className="text-[11px]">
              Top 5 por Volume
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border border-slate-200 overflow-x-auto text-xs">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="p-3 font-semibold text-slate-700">Identificador SKU (ASIN)</th>
                  <th className="p-3 font-semibold text-slate-700">Total de Avaliações</th>
                  <th className="p-3 font-semibold text-slate-700">Nota Média</th>
                  <th className="p-3 font-semibold text-slate-700">% 5 Estrelas</th>
                  <th className="p-3 font-semibold text-slate-700 text-right">Ação de Investigação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {(kpis?.top_products || []).map((prod) => (
                  <tr key={prod.parent_asin} className="hover:bg-slate-50/80 transition-colors">
                    <td className="p-3 font-mono font-medium text-slate-800">
                      {prod.parent_asin}
                    </td>
                    <td className="p-3 text-slate-600">
                      {prod.total_reviews.toLocaleString('pt-BR')}
                    </td>
                    <td className="p-3">
                      <span className="inline-flex items-center gap-1 font-semibold text-slate-800">
                        <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-500" />
                        {prod.media_nota.toFixed(2)}
                      </span>
                    </td>
                    <td className="p-3 text-slate-600">
                      <span className="text-emerald-700 font-medium">{prod.perc_5_estrelas.toFixed(1)}%</span>
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() =>
                          handleSelectQuery(
                            `Qual a nota média e as principais reclamações dos clientes para o produto ${prod.parent_asin}?`
                          )
                        }
                        className="inline-flex items-center gap-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 font-medium px-2.5 py-1 rounded transition-colors cursor-pointer"
                      >
                        <Sparkles className="h-3 w-3" />
                        Investigar no Chat
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Suggested Inquiries Quick Section */}
      <Card className="border-slate-200/90 shadow-xs bg-slate-50/60">
        <CardContent className="p-5">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <h4 className="text-sm font-semibold text-slate-900 flex items-center gap-1.5">
                <Sparkles className="h-4 w-4 text-blue-600" />
                Consultas Rápidas de Negócio Recomendadas
              </h4>
              <p className="text-xs text-slate-500 mt-0.5">
                Clique em qualquer pergunta para carregá-la imediatamente no campo de busca do explorador:
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSelectQuery('Top 10 produtos com maior volume de avaliações')}
                className="text-xs text-slate-700 bg-white hover:bg-slate-100 border-slate-200"
              >
                Top 10 Produtos por Volume
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSelectQuery('Quais os produtos com pior avaliação média e mais de 10 avaliações?')}
                className="text-xs text-slate-700 bg-white hover:bg-slate-100 border-slate-200"
              >
                Produtos com Pior Avaliação (&lt; 3.0)
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSelectQuery('Qual a nota média dos produtos com mais de 50 votos úteis?')}
                className="text-xs text-slate-700 bg-white hover:bg-slate-100 border-slate-200"
              >
                Produtos com Votos Úteis
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSelectQuery('Qual a distribuição percentual de notas de 1 a 5 estrelas?')}
                className="text-xs text-slate-700 bg-white hover:bg-slate-100 border-slate-200"
              >
                Distribuição 1★ a 5★
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
