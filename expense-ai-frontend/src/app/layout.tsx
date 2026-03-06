// src/app/layout.tsx
export const metadata = {
  title: 'Expense AI',
  description: 'Manage your expenses with Google Drive',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'sans-serif' }}>
        {children}
      </body>
    </html>
  )
}