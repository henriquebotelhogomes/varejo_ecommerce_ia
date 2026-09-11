export interface ChatResponseAPI {
  thread_id: string;
  intent: string;
  sql_query: string | null;
  sql_valid: boolean;
  data: Record<string, any>[] | null;
  final_response: string;
  next_best_actions: string[];
}

export interface YearlyTrendItem {
  ano: string;
  total: number;
  media_nota: number;
}

export interface TopProductItem {
  parent_asin: string;
  total_reviews: number;
  media_nota: number;
  perc_5_estrelas: number;
}

export interface KPIsResponseAPI {
  total_reviews: number;
  avg_rating: number;
  five_star_reviews: number;
  rating_distribution: Record<string, number>;
  yearly_trend?: YearlyTrendItem[];
  top_products?: TopProductItem[];
}

export interface HealthResponseAPI {
  status: string;
  version: string;
  database_ready: boolean;
}

const API_BASE = '/api/v1';

export async function sendChatMessage(query: string, threadId?: string | null): Promise<ChatResponseAPI> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, thread_id: threadId || undefined }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro de comunicação com o servidor' }));
    throw new Error(err.detail || `Erro HTTP ${res.status}`);
  }

  return res.json();
}

export async function sendChatMessageStream(
  query: string,
  threadId: string | null | undefined,
  onStep?: (msg: string) => void
): Promise<ChatResponseAPI> {
  const res = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, thread_id: threadId || undefined }),
  });

  if (!res.ok) {
    // Fallback para rota síncrona tradicional
    return sendChatMessage(query, threadId);
  }

  const reader = res.body?.getReader();
  if (!reader) return sendChatMessage(query, threadId);

  const decoder = new TextDecoder('utf-8');
  let finalResult: ChatResponseAPI | null = null;
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('data: ')) {
        let payload: any;
        try {
          payload = JSON.parse(trimmed.slice(6));
        } catch {
          continue; // Linha incompleta ou erro de parse ignorado
        }

        if (payload.type === 'step' && payload.message && onStep) {
          onStep(payload.message);
        } else if (payload.type === 'end') {
          finalResult = {
            thread_id: payload.thread_id,
            intent: payload.intent,
            sql_query: payload.sql_query,
            sql_valid: payload.sql_valid,
            data: payload.data,
            final_response: payload.final_response,
            next_best_actions: payload.next_best_actions,
          };
        } else if (payload.type === 'error') {
          throw new Error(payload.message || 'Erro durante a execução do agente.');
        }
      }
    }
  }

  if (!finalResult) {
    throw new Error('Falha ao decodificar a resposta do agente via stream.');
  }

  return finalResult;
}

export async function fetchKPIs(): Promise<KPIsResponseAPI> {
  const res = await fetch(`${API_BASE}/kpis`);
  if (!res.ok) {
    throw new Error(`Erro ao buscar KPIs: ${res.status}`);
  }
  return res.json();
}

export async function fetchHealth(): Promise<HealthResponseAPI> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    return { status: 'unreachable', version: 'unknown', database_ready: false };
  }
  return res.json();
}
