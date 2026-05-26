import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JobMatch AI — Semantic Resume Matching",
  description: "Upload your resume. Get AI-powered job matches ranked by semantic fit, skill overlap, and experience alignment.",
  keywords: ["job matching", "AI resume", "job search", "career"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}