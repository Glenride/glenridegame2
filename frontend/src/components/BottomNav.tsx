import { Home, BookOpen, User, Settings } from 'lucide-react';
import { motion } from 'framer-motion';
import WebApp from '@twa-dev/sdk';

interface BottomNavProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const BottomNav = ({ activeTab, setActiveTab }: BottomNavProps) => {
  const tabs = [
    { id: 'home', icon: Home, label: 'Home' },
    { id: 'story', icon: BookOpen, label: 'Story' },
    { id: 'profile', icon: User, label: 'Profile' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-tg-secondary-bg/90 backdrop-blur-md border-t border-tg-hint/20 pb-safe pt-2 px-6">
      <div className="flex justify-between items-center max-w-md mx-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => {
                WebApp.HapticFeedback.impactOccurred('light');
                setActiveTab(tab.id);
              }}
              className="relative flex flex-col items-center justify-center w-16 h-14"
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute -top-2 w-8 h-1 bg-brand-primary rounded-full"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
              <Icon 
                size={24} 
                className={`transition-colors duration-200 ${
                  isActive ? 'text-brand-primary' : 'text-tg-hint'
                }`} 
              />
              <span className={`text-[10px] mt-1 font-medium ${
                isActive ? 'text-brand-primary' : 'text-tg-hint'
              }`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
