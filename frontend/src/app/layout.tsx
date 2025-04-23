import './globals.css'; // ✅ 這是你專案 src/app/globals.css 裡引入 tailwind 的關鍵點

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <head>
        <script src="/svg-japan.js" />
      </head>
      <body className="antialiased text-gray-800 bg-gray-100">{children}</body>
    </html>
  );
}
