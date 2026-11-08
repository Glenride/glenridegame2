import { motion } from 'framer-motion';
import WebApp from '@twa-dev/sdk';

interface BrandedCardProps {
  title: string;
  value: string | number;
}

export const BrandedCard = ({ title, value }: BrandedCardProps) => {
  
  const handlePress = () => {
    // NATIVE FEEL: Trigger haptic feedback on interaction
    WebApp.HapticFeedback.impactOccurred('light');
  };

  return (
    <motion.div
      whileTap={{ scale: 0.98 }}
      onClick={handlePress}
      className="relative overflow-hidden rounded-2xl p-5 mb-4 shadow-lg"
      // Use Telegram's secondary background as base, but brand it with a border
      style={{ 
        backgroundColor: 'var(--tg-secondary-bg)',
        border: '1px solid var(--tg-hint)' 
      }}
    >
      {/* Decorative Brand Blob (Glassmorphism) */}
      <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-brand-primary opacity-20 blur-2xl" />

      <div className="relative z-10">
        <h3 className="text-sm font-medium text-tg-hint uppercase tracking-wider">
          {title}
        </h3>
        <p className="mt-1 text-3xl font-display font-bold text-tg-text">
          {value}
        </p>
      </div>
      
      {/* Custom Chevron using Brand Color */}
      <div className="absolute right-5 top-1/2 -translate-y-1/2 text-brand-primary">
        →
      </div>
    </motion.div>
  );
};
