import { gql } from '@apollo/client';

export const GET_CHANNELS = gql`
  query {
    channels {
      id
      name
      slug
      markup_percent
    }
  }
`;

export const SET_CHANNEL_MARKUP = gql`
  mutation SetChannelMarkup($input: ChannelMarkupInput!) {
    setChannelMarkup(input: $input) {
      success
      markup {
        channel_id
        markup_percent
      }
    }
  }
`;
