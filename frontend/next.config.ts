import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // @ts-ignore - Ignore type error if NextConfig types are outdated for this new feature
  allowedDevOrigins: [
    '10.228.181.110', 
    'localhost', 
    '127.0.0.1', 
    'witty-crews-mate.loca.lt', 
    '.loca.lt',
    '.trycloudflare.com',
    'knowing-tropical-covering-single.trycloudflare.com'
  ],
  
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*'
      }
    ];
  }
};

export default nextConfig;
