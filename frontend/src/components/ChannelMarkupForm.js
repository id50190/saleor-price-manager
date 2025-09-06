import React, { useState } from 'react';
import { useMutation } from '@apollo/client';
import { SET_CHANNEL_MARKUP } from '../queries';

const ChannelMarkupForm = ({ channel, token }) => {
  const [markup, setMarkup] = useState(channel.markup_percent || 0);
  const [setMarkup] = useMutation(SET_CHANNEL_MARKUP);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await setMarkup({
        variables: {
          input: {
            channelId: channel.id,
            markupPercent: parseFloat(markup)
          }
        },
        context: { headers: { Authorization: `Bearer ${token}` } }
      });
      alert('Markup updated successfully');
    } catch (error) {
      alert('Failed to update markup');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>{channel.name}</h3>
      <input
        type="number"
        value={markup}
        onChange={(e) => setMarkup(e.target.value)}
        min="0"
        step="0.01"
      />
      <button type="submit">Save</button>
    </form>
  );
};

export default ChannelMarkupForm;
