import "./globals.css";
import { Header } from "../components/ui";
export const metadata = { title: "HavenFind | Find a place that fits", description: "A grounded property search experience." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Header />
        <main>{children}</main>
      </body>
    </html>
  );
}
