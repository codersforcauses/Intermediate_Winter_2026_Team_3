import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;

// This is only used for the mock images.
module.exports = {
	images: {
		remotePatterns: [new URL('https://cdn.mos.cms.futurecdn.net/**')]
	},
}
