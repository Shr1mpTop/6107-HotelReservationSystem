import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Hotel Reservation Management System",
  description: "Professional hotel management system with modern web interface",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-US">
      <head>
        <meta httpEquiv="Content-Language" content="en" />
      </head>
      <body>{children}</body>
    </html>
  );
}
