/**
 * ChatWidget Wrapper for Root
 */

import React from 'react';
import ChatWidget from '../components/ChatWidget';

export function Root({ children }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
