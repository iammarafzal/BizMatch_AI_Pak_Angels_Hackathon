/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const rawBackend =
      process.env.BACKEND_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8000";
    const cleanBackend = rawBackend.replace(/\/api\/?$/, "").replace(/\/+$/, "");

    return [
      {
        source: "/api/:path*",
        destination: `${cleanBackend}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
