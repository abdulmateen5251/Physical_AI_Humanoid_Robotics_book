/**
 * ChatWidget Theme Plugin for Docusaurus
 * Injects ChatWidget globally across all documentation pages
 */

import React from 'react';
import ChatWidget from '../components/ChatWidget';

// ====================
// Plugin Root Component
// ====================

export default function ChatWidgetPlugin(context: any) {
  return {
    name: 'chat-widget-plugin',

    // Inject ChatWidget at the root level
    getClientModules() {
      return [];
    },
  };
}

// ====================
// Root Component Wrapper
// ====================

export function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
