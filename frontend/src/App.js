import React from 'react';
import { ApolloProvider } from '@apollo/client';
import { createApolloClient } from '@saleor/app-sdk/apollo';
import { AppBridgeProvider } from '@saleor/app-sdk/app-bridge';
import PriceManager from './pages/PriceManager';

const App = () => {
  const client = createApolloClient({
    apiUrl: process.env.REACT_APP_API_URL,
  });

  return '<AppBridgeProvider><ApolloProvider client={client}><PriceManager /></ApolloProvider></AppBridgeProvider>';
};

export default App;
