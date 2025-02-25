import { extendTheme } from '@chakra-ui/react';

const config = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
};

const fonts = {
  heading: "'Poppins', sans-serif",
  body: "'Inter', sans-serif",
};

const colors = {
  brand: {
    50: '#f5e9ff',
    100: '#dac1ff',
    200: '#c098ff',
    300: '#a46eff',
    400: '#8a45ff',
    500: '#712bff',
    600: '#5a20cc',
    700: '#431799',
    800: '#2c0e66',
    900: '#160533',
  },
};

const components = {
  Button: {
    baseStyle: {
      fontWeight: 'bold',
      borderRadius: 'lg',
    },
    variants: {
      solid: {
        bg: 'brand.500',
        color: 'white',
        _hover: {
          bg: 'brand.600',
        },
      },
    },
  },
};

export const theme = extendTheme({
  config,
  fonts,
  colors,
  components,
  styles: {
    global: {
      body: {
        bg: 'gray.900',
        color: 'white',
      },
    },
  },
}); 