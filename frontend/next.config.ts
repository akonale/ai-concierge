import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone', // <--- Ensure this line is present
  reactStrictMode: true, // Example other option
  // Add other configurations like typescript, eslint if not already handled by create-next-app setup
};

export default nextConfig;
