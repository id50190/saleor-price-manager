import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

const PriceManager = () => {
  const [channels, setChannels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [calculation, setCalculation] = useState(null);

  // Load channels on component mount
  useEffect(() => {
    fetchChannels();
  }, []);

  const fetchChannels = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/channels/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setChannels(data);
      setError(null);
    } catch (err) {
      setError(`Failed to fetch channels: ${err.message}`);
      console.error('Error fetching channels:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateMarkup = async (channelId, newMarkup) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/channels/markup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          channel_id: channelId,
          markup_percent: parseFloat(newMarkup)
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Refresh channels list
      await fetchChannels();
      alert('✅ Markup updated successfully!');
    } catch (err) {
      alert(`❌ Failed to update markup: ${err.message}`);
      console.error('Error updating markup:', err);
    }
  };

  const calculatePrice = async (channelId, basePrice) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/prices/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: 'demo_product',
          channel_id: channelId,
          base_price: parseFloat(basePrice)
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setCalculation(data);
    } catch (err) {
      alert(`❌ Failed to calculate price: ${err.message}`);
      console.error('Error calculating price:', err);
    }
  };

  if (loading) {
    return <div>🔄 Loading channels...</div>;
  }

  if (error) {
    return (
      <div>
        <h3>❌ Error</h3>
        <p>{error}</p>
        <p>Make sure the FastAPI backend is running on http://localhost:8000</p>
        <button onClick={fetchChannels}>🔄 Retry</button>
      </div>
    );
  }

  return (
    <div>
      <h2>📊 Channel Management</h2>
      
      {channels.length === 0 ? (
        <p>No channels available</p>
      ) : (
        channels.map(channel => (
          <div key={channel.id} className="channel-card">
            <h3>🏪 {channel.name}</h3>
            <p><strong>Slug:</strong> {channel.slug}</p>
            <p><strong>Current Markup:</strong> {channel.markup_percent}%</p>
            
            <div className="markup-form">
              <label>Update Markup:</label>
              <input 
                type="number" 
                className="markup-input"
                placeholder="15.5"
                step="0.1"
                min="0"
                max="100"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    updateMarkup(channel.id, e.target.value);
                  }
                }}
              />
              <span>%</span>
              <button 
                className="update-btn"
                onClick={(e) => {
                  const input = e.target.previousElementSibling.previousElementSibling;
                  updateMarkup(channel.id, input.value);
                }}
              >
                💾 Update
              </button>
            </div>
            
            <div className="markup-form">
              <label>Test Price Calculation:</label>
              <input 
                type="number" 
                className="markup-input"
                placeholder="100.00"
                step="0.01"
                min="0"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    calculatePrice(channel.id, e.target.value);
                  }
                }}
              />
              <span>$</span>
              <button 
                className="update-btn"
                onClick={(e) => {
                  const input = e.target.previousElementSibling.previousElementSibling;
                  calculatePrice(channel.id, input.value);
                }}
              >
                🧮 Calculate
              </button>
            </div>
          </div>
        ))
      )}
      
      {calculation && (
        <div className="channel-card" style={{ backgroundColor: '#e8f5e8' }}>
          <h3>🧮 Price Calculation Result</h3>
          <p><strong>Base Price:</strong> ${calculation.base_price}</p>
          <p><strong>Markup:</strong> {calculation.markup_percent}%</p>
          <p><strong>Final Price:</strong> <span style={{ fontSize: '1.2em', fontWeight: 'bold', color: '#0070f3' }}>${calculation.final_price}</span></p>
        </div>
      )}
      
      <div style={{ marginTop: '30px', textAlign: 'center' }}>
        <p>💡 <strong>Demo Mode:</strong> Changes are simulated and won't persist</p>
        <p>🔗 <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">Open API Documentation</a></p>
      </div>
    </div>
  );
};

export default PriceManager;