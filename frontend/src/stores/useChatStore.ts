import { create } from 'zustand';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sqlQuery?: string | null;
  sqlValid?: boolean;
  data?: Record<string, any>[] | null;
  nextBestActions?: string[];
  intent?: string;
  timestamp: string;
}

interface ChatStore {
  messages: ChatMessage[];
  threadId: string | null;
  isLoading: boolean;
  activeTab: 'chat' | 'dashboard' | 'finops';
  totalQueries: number;
  estimatedSavingsUsd: number;
  draftQuery: string;
  setActiveTab: (tab: 'chat' | 'dashboard' | 'finops') => void;
  setThreadId: (id: string) => void;
  setDraftQuery: (draftQuery: string) => void;
  addMessage: (msg: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  setIsLoading: (loading: boolean) => void;
  updateFinOps: (savings: number) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Olá! Sou o **RetailSense**, seu console analítico de Customer Experience e Varejo.\n\n' +
        'Estou conectado à base com **204.382 avaliações da Amazon**. Você pode me fazer perguntas quantitativas (médias, rankings) ou investigar motivos de insatisfação dos clientes.\n\n' +
        'Clique em uma das sugestões abaixo para carregar a pergunta no campo de busca ou digite diretamente!',
      nextBestActions: [
        'Qual é a nota média geral das avaliações?',
        'Quais os 5 produtos com maior volume de avaliações?',
        'Qual a distribuição percentual de notas de 1 a 5 estrelas?'
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ],
  threadId: null,
  isLoading: false,
  activeTab: 'dashboard',
  totalQueries: 0,
  estimatedSavingsUsd: 0.0,
  draftQuery: '',

  setActiveTab: (activeTab) => set({ activeTab }),
  setThreadId: (threadId) => set({ threadId }),
  setDraftQuery: (draftQuery) => set({ draftQuery }),
  addMessage: (msg) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...msg,
          id: `msg_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ],
    })),
  setIsLoading: (isLoading) => set({ isLoading }),
  updateFinOps: (savings) =>
    set((state) => ({
      totalQueries: state.totalQueries + 1,
      estimatedSavingsUsd: state.estimatedSavingsUsd + savings,
    })),
  clearChat: () =>
    set({
      messages: [],
      threadId: null,
    }),
}));
