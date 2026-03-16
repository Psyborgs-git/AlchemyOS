import type React from "react";

const appStyles: React.CSSProperties = {
  margin: "2rem auto",
  maxWidth: "720px",
  fontFamily: "Inter, system-ui, -apple-system, sans-serif",
  lineHeight: 1.5,
};

function App() {
  return (
    <main style={appStyles}>
      <h1>🧪 AlchemyOS</h1>
      <p>Phase 0 scaffolding is active.</p>
      <p>Backend health endpoint: http://localhost:8000/v1/health</p>
    </main>
  );
}

export default App;
