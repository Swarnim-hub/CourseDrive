/** @type {iMPORT('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['images.unsplash.com', 'lh3.googleusercontent.com', 'avatars.githubusercontent.com', 'localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      }
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/:path*` : 'http://localhost:8000/api/v1/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
