import type { Config } from "tailwindcss";
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: { colors: { ink: "#132238", teal: "#147d77", sand: "#f7f5ef" }, boxShadow: { soft: "0 10px 35px rgba(19,34,56,.08)" } } },
  plugins: []
};
export default config;
