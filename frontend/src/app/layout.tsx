import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'PeopleDoxx — Verificación de Identidad Pública',
  description:
    'Consulta información pública de ciudadanos ecuatorianos desde fuentes gubernamentales oficiales: SRI, SATJE, SUPA, IESS y CNE.',
  keywords: ['OSINT', 'Ecuador', 'cédula', 'SRI', 'IESS', 'SATJE', 'CNE', 'consulta pública'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-slate-900 text-slate-100 antialiased">
        <Navbar />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
