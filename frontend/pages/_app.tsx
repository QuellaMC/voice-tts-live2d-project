import { ChakraProvider } from '@chakra-ui/react';
import type { AppProps } from 'next/app';
import React from 'react';
import { theme } from '../styles/theme';
import '../styles/globals.css';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ChakraProvider theme={theme}>
      <Component {...pageProps} />
    </ChakraProvider>
  );
}

export default MyApp; 