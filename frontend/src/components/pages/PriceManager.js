import React, { useState, useEffect } from 'react';
import { useAppBridge } from '@saleor/app-sdk/app-bridge';
import { useQuery } from '@apollo/client';
import { GET_CHANNELS } from '../queries';
import ChannelMarkupForm from '../components/ChannelMarkupForm';

const PriceManager = () => {
  const { appBridgeState } = useAppBridge();
  const { data, loading, error } = useQuery(GET_CHANNELS, {
    context: { headers: { Authorization: `Bearer ${appBridgeState?.token}` } }
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h1>Price Manager</h1>
      {data.channels.map((channel) => (
        <ChannelMarkupForm
          key={channel.id}
          channel={channel}
          token={appBridgeState?.token}
        />
      ))}
    </div>
  );
};

export default PriceManager;
