import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import WebApp from '@twa-dev/sdk';

interface ActionCardProps {
  title: string;
  subtitle?: string;
  icon?: LucideIcon;
  value?: string;
  variant?: 'default' | 'primary' | 'success';
  onClick?: () => void;
}

export const ActionCard = ({ 
  title, 
  subtitle, 
  icon: Icon, 
  value, 
  variant = 'default',
  onClick 
}: ActionCardProps) => {
  
  const handlePress = () => {
    WebApp.HapticFeedback.impactOccurred('medium');
    onClick?.();
  };

  const bgClass = variant === 'primary' ? 'bg-brand-primary text-white' : 
                 variant === 'success' ? 'bg-brand-accent text-white' : 
                 'bg-tg-secondary-bg text-tg-text';

  const textClass = variant === 'default' ? 'text-tg-text' : 'text-white';
  const subtextClass = variant === 'default' ? 'text-tg-hint' : 'text-white/80';

  return (
    <motion.button
      whileTap={{ scale: 0.98 }}
      onClick={handlePress}
      className={`w-full text-left relative overflow-hidden rounded-2xl p-4 shadow-sm border border-tg-hint/10 ${bgClass}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {Icon && (
            <div className={`p-2 rounded-xl ${variant === 'default' ? 'bg-tg-bg' : 'bg-white/20'}`}>
              <Icon size={20} className={textClass} />
            </div>
          )}
          <div>
            <h3 className={`font-semibold text-sm ${textClass}`}>
              {title}
            </h3>
            {subtitle && (
              <p className={`text-xs ${subtextClass}`}>
                {subtitle}
              </p>
            )}
          </div>
        </div>
        
        {value && (
          <span className={`font-display font-bold text-lg ${textClass}`}>
            {value}
          </span>
        )}
      </div>
    </motion.button>
  );
};
