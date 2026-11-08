import { useState } from 'react';
import { useTelegramTheme } from './hooks/useTelegramTheme';
import { BottomNav } from './components/BottomNav';
import { ActionCard } from './components/ActionCard';
import { Sparkles, Heart, ScrollText, Wallet, ChevronRight } from 'lucide-react';

function App() {
  useTelegramTheme();
  const [activeTab, setActiveTab] = useState('home');

  return (
    <div className="min-h-screen bg-tg-bg text-tg-text font-display pb-24">
      {/* Header Section */}
      <header className="pt-6 pb-2 px-4 bg-gradient-to-b from-tg-secondary-bg/50 to-transparent">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-tg-hint text-xs font-medium uppercase tracking-wider mb-1">Currently Playing</p>
            <h1 className="text-2xl font-bold text-tg-text">Chapter 1: Arrival</h1>
          </div>
          <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-brand-primary to-brand-accent flex items-center justify-center shadow-lg">
            <span className="text-white font-bold">G</span>
          </div>
        </div>

        {/* Main Stats Cards */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <div className="bg-tg-secondary-bg p-4 rounded-2xl border border-tg-hint/10">
            <div className="flex items-center gap-2 mb-2">
              <Heart size={16} className="text-brand-primary fill-brand-primary" />
              <span className="text-xs text-tg-hint font-medium">Affinity</span>
            </div>
            <span className="text-2xl font-bold">84%</span>
          </div>
          <div className="bg-tg-secondary-bg p-4 rounded-2xl border border-tg-hint/10">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles size={16} className="text-brand-accent" />
              <span className="text-xs text-tg-hint font-medium">Karma</span>
            </div>
            <span className="text-2xl font-bold">1,250</span>
          </div>
        </div>
      </header>

      {/* Scrollable Content */}
      <main className="px-4 space-y-6">
        {/* Quick Actions */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold">Actions</h2>
            <button className="text-brand-primary text-sm font-medium">View all</button>
          </div>
          <div className="space-y-3">
            <ActionCard 
              title="Continue Story" 
              subtitle="Resume from checkpoint" 
              icon={ScrollText} 
              variant="primary"
            />
            <ActionCard 
              title="Daily Rewards" 
              subtitle="Claim your bonus" 
              icon={Wallet} 
              value="+50"
              variant="success"
            />
          </div>
        </section>

        {/* Recent Quests */}
        <section>
          <h2 className="text-lg font-bold mb-3">Active Quests</h2>
          <div className="bg-tg-secondary-bg rounded-2xl overflow-hidden border border-tg-hint/10">
            {[
              { title: 'Meet Calvin at the Cafe', reward: '50 XP' },
              { title: 'Find the Hidden Letter', reward: 'Key Item' },
              { title: 'Impress Jackson', reward: '+10 Affinity' }
            ].map((quest, i) => (
              <div key={i} className="flex items-center justify-between p-4 border-b border-tg-hint/5 last:border-0 active:bg-tg-bg/50 transition-colors">
                <div>
                  <h4 className="font-medium text-sm">{quest.title}</h4>
                  <span className="text-xs text-brand-accent font-medium">{quest.reward}</span>
                </div>
                <ChevronRight size={16} className="text-tg-hint" />
              </div>
            ))}
          </div>
        </section>
      </main>

      <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
    </div>
  );
}

export default App;
