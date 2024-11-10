import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/videos/:path*",
        destination: "/api/videos/:path*",
      },
      { source: "/annotations/:id", destination: "/api/annotations/:id" },
    ];
  },
};

export default nextConfig;
