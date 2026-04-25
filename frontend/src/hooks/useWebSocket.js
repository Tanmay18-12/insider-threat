import React, { useEffect } from 'react';
import { useAlertStore } from '../store/useAuthStore';

export const useWebSocket = (url) => {
  const addAlert = useAlertStore(state => state.addAlert);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        addAlert(data);
      } catch (e) {
        console.error("WS parse error", e);
      }
    };

    return () => {
      ws.close();
    };
  }, [url, addAlert]);
};
