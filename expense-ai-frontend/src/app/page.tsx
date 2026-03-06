// src/app/page.tsx
'use client';
import { driveService } from '../services/driveService';

export default function HomePage() {
  const handleConnect = async () => {
    const url = await driveService.getAuthUrl();
    // Redirects the entire browser tab to Django's Google Auth view
    window.location.href = url; 
  };

  return (
    <main style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      height: '100vh' 
    }}>
      <h1>Expense AI</h1>
      <p>Connect your Google Drive to start processing expenses.</p>
      <button 
        onClick={handleConnect}
        style={{
          padding: '12px 24px',
          backgroundColor: '#4285F4',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '16px'
        }}
      >
        Connect Google Drive
      </button>
    </main>
  );
}