import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Veritas — Citation-Verified Literature Review Generator",
  description: "Generate grounded, streaming literature reviews where every claim is verified against its cited paper.",
  openGraph: {
    title: "Veritas — Citation-Verified Literature Reviews",
    description: "Every claim checked. Supported, Partial, Unsupported verdicts with verbatim quotes and interactive citation graph.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var stored = localStorage.getItem('veritas-theme');
                  var supportDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                  if (stored === 'dark' || (!stored && supportDark)) {
                    document.documentElement.classList.add('dark');
                  } else {
                    document.documentElement.classList.remove('dark');
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-screen bg-background text-text-primary antialiased selection:bg-accent selection:text-white">
        {children}
      </body>
    </html>
  );
}
