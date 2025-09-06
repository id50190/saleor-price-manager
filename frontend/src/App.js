import React, { useState, useEffect } from 'react';
import PriceManager from './components/PriceManager';

const App = () => {
  return (
    <div className="container">
      <div className="header">
        <h1>🚀 Saleor Price Manager</h1>
        <span className="demo-badge">DEMO MODE</span>
        <p>FastAPI microservice for dynamic multi-channel pricing</p>
      </div>
      
      <div className="api-info">
        <h3>📡 API Information</h3>
        <p><strong>Backend:</strong> http://localhost:8000</p>
        <p><strong>Swagger UI:</strong> <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a></p>
        <p><strong>Health Check:</strong> <a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer">http://localhost:8000/health</a></p>
      </div>

      <PriceManager />
    </div>
  );
};

export default App;
