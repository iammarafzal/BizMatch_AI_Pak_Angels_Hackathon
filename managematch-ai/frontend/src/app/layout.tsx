import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ManageMatch AI | Pak Angels Hackathon",
  description: "Explainable decision-support for executive hiring.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} bg-obsidian text-slate-200 antialiased min-h-screen flex flex-col`}>
        <div className="flex-grow">
          {children}
        </div>
        
        {/* Human-in-the-Loop Footer Rule #6 */}
        <div className="bg-obsidian border-t border-white/10 py-4 px-6 mt-auto">
          <div className="max-w-7xl mx-auto flex items-center justify-center text-center">
            <p className="text-xs text-slate-500 max-w-3xl">
              <strong className="text-slate-400">ManageMatch AI is a decision-support platform.</strong> Recommendations provide advisory trade-off analysis; final hiring choices remain with the founder. 
            </p>
          </div>
        </div>
      </body>
    </html>
  );
}
