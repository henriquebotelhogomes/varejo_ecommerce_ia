import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Search, Download, Code2, Database, ShieldCheck, ArrowRight, CornerDownLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Card, CardContent } from './ui/card';
import { useChatStore, ChatMessage } from '../stores/useChatStore';
import { sendChatMessageStream } from '../services/api';
import { SqlInspectionModal } from './SqlInspectionModal';

export const ChatView: React.FC = () => {
  const {
    messages,
    threadId,
    isLoading,
    draftQuery,
    addMessage,
    setIsLoading,
    setThreadId,
    setDraftQuery,
    updateFinOps,
  } = useChatStore();
  const [inputValue, setInputValue] = useState('');
  const [openTableMsgId, setOpenTableMsgId] = useState<string | null>(null);
  const [inspectingMsg, setInspectingMsg] = useState<ChatMessage | null>(null);
  const [streamStatus, setStreamStatus] = useState<string>(
    'Executando consulta analítica com validação AST no DuckDB...'
  );
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sincroniza perguntas vindas do Dashboard ou sugestões externas
  useEffect(() => {
    if (draftQuery) {
      setInputValue(draftQuery);
      setDraftQuery('');
      setTimeout(() => {
        inputRef.current?.focus();
        inputRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 60);
    }
  }, [draftQuery, setDraftQuery]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSelectSuggestion = (text: string) => {
    setInputValue(text);
    setTimeout(() => {
      inputRef.current?.focus();
      inputRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 50);
  };

  const handleSend = async (queryText?: string) => {
    const text = queryText || inputValue;
    if (!text.trim() || isLoading) return;

    // Adiciona requisição de consulta do usuário
    addMessage({
      role: 'user',
      content: text.trim(),
    });
    setInputValue('');
    setIsLoading(true);
    setStreamStatus('Iniciando análise com DuckDB...');

    try {
      const res = await sendChatMessageStream(text.trim(), threadId, (statusMsg) => {
        setStreamStatus(statusMsg);
      });
      if (res.thread_id) {
        setThreadId(res.thread_id);
      }

      // Adiciona resultado analítico
      addMessage({
        role: 'assistant',
        content: res.final_response,
        sqlQuery: res.sql_query,
        sqlValid: res.sql_valid,
        data: res.data,
        nextBestActions: res.next_best_actions,
        intent: res.intent,
      });

      updateFinOps(0.0125);
    } catch (err: any) {
      addMessage({
        role: 'assistant',
        content: `❌ Erro ao processar consulta: ${err.message || 'Falha de comunicação com o backend.'}`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const exportToCSV = (data: Record<string, any>[], filename = 'relatorio_analitico.csv') => {
    if (!data || data.length === 0) return;
    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(','),
      ...data.map((row) =>
        headers.map((h) => `"${String(row[h] ?? '').replace(/"/g, '""')}"`).join(',')
      ),
    ];
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const quickQueries = [
    'Top 5 produtos com maior volume de avaliações',
    'Qual a nota média dos produtos com mais de 50 votos úteis?',
    'Distribuição percentual de notas de 1 a 5 estrelas',
    'Quais os produtos com pior avaliação média e mais de 10 avaliações?',
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Query Console Bar */}
      <Card className="border-slate-200/90 shadow-sm bg-white">
        <CardContent className="p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Explorador de Dados & Consultas em Linguagem Natural
              </h3>
              <p className="text-xs text-slate-500">
                Geração automática de SQL seguro com AST Guardrail sobre a tabela <code className="text-slate-700 bg-slate-100 px-1 py-0.5 rounded font-mono text-[11px]">avaliacoes</code> (DuckDB / Parquet)
              </p>
            </div>
            <Badge variant="neutral" className="text-[11px]">
              Motor: DuckDB Colunar (SIMD)
            </Badge>
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-400" />
              <Input
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ex: Quais são os 10 produtos mais bem avaliados com mais de 20 reviews?"
                disabled={isLoading}
                className="pl-10 h-11 bg-slate-50/50 border-slate-300 focus:bg-white text-slate-900 text-sm"
              />
            </div>
            <Button
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              size="md"
              className="gap-2 shrink-0 bg-blue-600 hover:bg-blue-700 text-white font-medium"
            >
              <CornerDownLeft className="h-4 w-4" />
              Executar Análise
            </Button>
          </form>

          {/* Quick Business Query Chips */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] font-medium text-slate-400 mr-1">Consultas Rápidas:</span>
            {quickQueries.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectSuggestion(q)}
                disabled={isLoading}
                className="text-left text-xs bg-slate-100 hover:bg-slate-200 hover:text-slate-900 text-slate-600 border border-slate-200/80 rounded-md px-2.5 py-1 transition-all disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Query Results & History Area */}
      <div className="space-y-5">
        {messages.length === 0 && (
          <div className="text-center py-12 px-4 rounded-xl border border-dashed border-slate-300 bg-white">
            <Database className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <h4 className="text-sm font-semibold text-slate-700">Nenhuma consulta realizada na sessão</h4>
            <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
              Selecione uma das consultas rápidas acima ou digite uma pergunta de negócio para analisar o catálogo em tempo real.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className="space-y-2">
            {msg.role === 'user' ? (
              <div className="flex items-center gap-2 pt-2">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Consulta Solicitada:
                </span>
                <span className="text-sm font-medium text-slate-900 bg-slate-100 px-3 py-1 rounded-md border border-slate-200">
                  {msg.content}
                </span>
              </div>
            ) : (
              <Card className="border-slate-200/90 shadow-sm bg-white overflow-hidden">
                <div className="bg-slate-50/80 px-5 py-3 border-b border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-700">
                      Relatório Analítico Executivo
                    </span>
                    {msg.intent && (
                      <Badge variant="neutral" className="text-[10px]">
                        {msg.intent}
                      </Badge>
                    )}
                  </div>
                  {msg.sqlValid !== undefined && (
                    <Badge variant={msg.sqlValid ? 'success' : 'warning'} className="text-[10px]">
                      <ShieldCheck className="h-3 w-3" />
                      {msg.sqlValid ? 'AST Guardrail: SELECT Validado' : 'Validação AST'}
                    </Badge>
                  )}
                </div>

                <CardContent className="p-5 space-y-4">
                  {/* Resposta Executiva Formatada */}
                  <div className="prose prose-slate prose-sm max-w-none text-slate-800 leading-relaxed">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>

                  {/* Barra de Ações & Dados */}
                  {(msg.sqlQuery || (msg.data && msg.data.length > 0)) && (
                    <div className="space-y-3 pt-2">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                          <Database className="h-3.5 w-3.5 text-slate-500" />
                          {msg.data && msg.data.length > 0
                            ? `Registros Retornados (${msg.data.length} linhas)`
                            : 'Consulta Analítica Concluída'}
                        </span>
                        <div className="flex items-center gap-2">
                          {msg.sqlQuery && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setInspectingMsg(msg)}
                              className="text-xs text-slate-700 bg-white hover:bg-slate-50 border-slate-200"
                            >
                              <Code2 className="h-3.5 w-3.5 mr-1.5 text-blue-600" />
                              Inspecionar Consulta
                            </Button>
                          )}
                          {msg.data && msg.data.length > 0 && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setOpenTableMsgId(openTableMsgId === msg.id ? null : msg.id)}
                                className="text-xs text-slate-700 bg-white hover:bg-slate-50 border-slate-200"
                              >
                                {openTableMsgId === msg.id ? 'Ocultar Tabela' : 'Visualizar Tabela'}
                              </Button>
                              <Button
                                variant="secondary"
                                size="sm"
                                onClick={() => exportToCSV(msg.data!)}
                                className="text-xs font-medium"
                              >
                                <Download className="h-3.5 w-3.5 mr-1" />
                                Exportar CSV
                              </Button>
                            </>
                          )}
                        </div>
                      </div>

                      {openTableMsgId === msg.id && msg.data && msg.data.length > 0 && (
                        <div className="rounded-lg border border-slate-200 overflow-x-auto max-h-72 text-xs">
                          <table className="w-full text-left border-collapse">
                            <thead className="bg-slate-50 border-b border-slate-200 sticky top-0">
                              <tr>
                                {Object.keys(msg.data[0]).map((col) => (
                                  <th key={col} className="p-2.5 font-semibold text-slate-700">{col}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 bg-white">
                              {msg.data.map((row, idx) => (
                                <tr key={idx} className="hover:bg-slate-50/80">
                                  {Object.values(row).map((val: any, cidx) => (
                                    <td key={cidx} className="p-2.5 text-slate-600 truncate max-w-xs">{String(val)}</td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Sugestões de Próximas Análises (Next Best Action) */}
                  {msg.nextBestActions && msg.nextBestActions.length > 0 && (
                    <div className="pt-3 border-t border-slate-100 space-y-2">
                      <span className="text-xs font-semibold text-slate-700 block">
                        Aprofundamentos Analíticos Recomendados:
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {msg.nextBestActions.map((action, i) => (
                          <button
                            key={i}
                            onClick={() => handleSelectSuggestion(action)}
                            disabled={isLoading}
                            className="text-left text-xs bg-slate-50 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 border border-slate-200 rounded-md px-3 py-1.5 transition-all text-slate-700 disabled:opacity-50 flex items-center gap-1.5 cursor-pointer shadow-xs"
                          >
                            <ArrowRight className="h-3 w-3 text-blue-600 shrink-0" />
                            {action}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        ))}

        {isLoading && (
          <Card className="border-slate-200 bg-white p-4">
            <div className="flex items-center gap-3 text-slate-600 text-xs">
              <div className="h-4 w-4 rounded-full border-2 border-blue-600 border-t-transparent animate-spin shrink-0" />
              <span className="font-medium text-slate-700">{streamStatus}</span>
            </div>
          </Card>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Modal de Inspeção de Consulta SQL & Metadados */}
      {inspectingMsg && inspectingMsg.sqlQuery && (
        <SqlInspectionModal
          isOpen={true}
          onClose={() => setInspectingMsg(null)}
          sqlQuery={inspectingMsg.sqlQuery}
          sqlValid={inspectingMsg.sqlValid}
          rowCount={inspectingMsg.data?.length}
          intent={inspectingMsg.intent}
        />
      )}
    </div>
  );
};
