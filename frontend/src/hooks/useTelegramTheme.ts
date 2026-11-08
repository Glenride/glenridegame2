import { useEffect } from 'react';
import WebApp from '@twa-dev/sdk';

// Check if we're running inside Telegram
const isTelegramWebApp = () => {
  try {
    return WebApp.initData !== '' || WebApp.platform !== 'unknown';
  } catch {
    return false;
  }
};

export const useTelegramTheme = () => {
  useEffect(() => {
    const root = document.documentElement;

    // Default fallback theme for browser testing
    const applyFallbackTheme = () => {
      root.style.setProperty('--tg-bg', '#1a1a2e');
      root.style.setProperty('--tg-text', '#ffffff');
      root.style.setProperty('--tg-hint', '#8b8b9e');
      root.style.setProperty('--tg-link', '#6c5ce7');
      root.style.setProperty('--tg-button', '#6c5ce7');
      root.style.setProperty('--tg-button-text', '#ffffff');
      root.style.setProperty('--tg-secondary-bg', '#25253a');
    };

    try {
      if (isTelegramWebApp()) {
        // Running inside Telegram
        WebApp.ready();
        WebApp.expand();

        const applyTheme = () => {
          const theme = WebApp.themeParams;
          root.style.setProperty('--tg-bg', theme.bg_color || '#1a1a2e');
          root.style.setProperty('--tg-text', theme.text_color || '#ffffff');
          root.style.setProperty('--tg-hint', theme.hint_color || '#8b8b9e');
          root.style.setProperty('--tg-link', theme.link_color || '#6c5ce7');
          root.style.setProperty('--tg-button', theme.button_color || '#6c5ce7');
          root.style.setProperty('--tg-button-text', theme.button_text_color || '#ffffff');
          root.style.setProperty('--tg-secondary-bg', theme.secondary_bg_color || '#25253a');
        };

        applyTheme();
        WebApp.onEvent('themeChanged', applyTheme);
      } else {
        // Running in browser - apply fallback theme
        applyFallbackTheme();
      }
    } catch (error) {
      console.warn('Telegram WebApp SDK not available, using fallback theme');
      applyFallbackTheme();
    }
  }, []);
};
