import { ChakraProvider } from '@chakra-ui/react';
import type { NextComponentType } from 'next';
import React from 'react';
import { theme } from '../styles/theme';
import '../styles/globals.css';

type MyAppProps = {
  Component: NextComponentType;
  pageProps: Record<string, unknown>;
};

function MyApp({ Component, pageProps }: MyAppProps) {
  return (
    <ChakraProvider theme={theme}>
      <Component {...pageProps} />
    </ChakraProvider>
  );
}

export default MyApp; 