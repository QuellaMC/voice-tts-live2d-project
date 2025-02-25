/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost', 'example.com'], // Add any domains you'll load images from
  },
  webpack: (config, { isServer }) => {
    // Allow importing Live2D model files and audio files
    config.module.rules.push({
      test: /\.(moc3|model3\.json|physics3\.json|pose3\.json|cdi3\.json|ogg|mp3|wav)$/,
      type: 'asset/resource',
    });

    // Important for WebSocket and Live2D support
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    return config;
  },
  env: {
    // Public environment variables
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

module.exports = nextConfig; 