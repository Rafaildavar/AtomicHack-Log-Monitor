// Simplified App for debugging
export default function App() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#0A0E27',
      color: 'white',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      gap: '20px',
      padding: '20px'
    }}>
      <h1 style={{ fontSize: '48px', margin: 0 }}>✅ React Works!</h1>
      <p style={{ fontSize: '24px', color: '#00D4FF' }}>AtomicHack Log Monitor</p>
      <p style={{ color: '#888' }}>If you see this, React is rendering correctly</p>
      
      <div style={{ 
        marginTop: '40px',
        padding: '20px',
        background: 'rgba(255,255,255,0.1)',
        borderRadius: '8px'
      }}>
        <p style={{ margin: 0, color: '#ccc' }}>
          Now let's check what went wrong with the full app...
        </p>
      </div>
    </div>
  );
}

