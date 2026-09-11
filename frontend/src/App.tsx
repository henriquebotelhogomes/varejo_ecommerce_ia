import React from 'react';
import { Header } from './components/Header';
import { DashboardView } from './components/DashboardView';
import { ChatView } from './components/ChatView';
import { FinOpsView } from './components/FinOpsView';
import { useChatStore } from './stores/useChatStore';

export const App: React.FC = () => {
  const { activeTab } = useChatStore();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans antialiased">
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
        {activeTab === 'dashboard' && <DashboardView />}
        {activeTab === 'chat' && <ChatView />}
        {activeTab === 'finops' && <FinOpsView />}
      </main>
    </div>
  );
};

export default App;
