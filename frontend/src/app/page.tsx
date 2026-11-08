import { SearchForm } from '@/components/SearchForm';

interface Feature {
  code: string;
  name: string;
  description: string;
}

const FEATURES: Feature[] = [
  {
    code: 'SRI',
    name: 'Servicio de Rentas Internas',
    description: 'Datos tributarios, RUC, actividad económica y estado contribuyente.',
  },
  {
    code: 'SATJE',
    name: 'Función Judicial',
    description: 'Causas judiciales activas y cerradas en el sistema judicial ecuatoriano.',
  },
  {
    code: 'SUPA',
    name: 'Sistema de Pensiones',
    description: 'Nómina pública, cargo, institución y remuneración en el sector público.',
  },
  {
    code: 'IESS',
    name: 'Seguridad Social',
    description: 'Historial de afiliación, aportaciones y beneficios de seguridad social.',
  },
  {
    code: 'CNE',
    name: 'Consejo Nacional Electoral',
    description: 'Padrón electoral, lugar de votación y registro de sufragio.',
  },
  {
    code: 'MDT',
    name: 'Ministerio del Trabajo',
    description: 'Historial laboral, empleadores y contratos en el Ministerio de Trabajo.',
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-64px)]">
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center px-4 pt-20 pb-16 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-orange-500/30 bg-orange-500/10 px-4 py-1.5 text-sm text-orange-400">
          <span className="h-2 w-2 rounded-full bg-orange-500 animate-pulse" />
          Fuentes gubernamentales ecuatorianas
        </div>

        <h1 className="mt-4 text-5xl font-extrabold tracking-tight text-white sm:text-6xl lg:text-7xl">
          People<span className="text-orange-500">Doxx</span>
        </h1>

        <p className="mt-6 max-w-2xl text-lg text-slate-400 sm:text-xl">
          Consulta información pública desde fuentes gubernamentales ecuatorianas.
          Ingresa una cédula para generar un reporte consolidado en segundos.
        </p>

        <div className="mt-10 w-full max-w-lg">
          <SearchForm />
        </div>
      </section>

      {/* Features Grid */}
      <section className="px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <h2 className="mb-10 text-center text-2xl font-bold text-slate-200">
            Fuentes de información
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((feature) => (
              <div
                key={feature.code}
                className="rounded-xl border border-slate-700 bg-slate-800 p-6 shadow-lg hover:border-orange-500/50 hover:shadow-orange-500/5"
              >
                <div className="mb-3 inline-block rounded bg-orange-500/10 px-2.5 py-1 text-xs font-bold text-orange-400">
                  {feature.code}
                </div>
                <h3 className="mb-1 text-lg font-semibold text-white">{feature.name}</h3>
                <p className="text-sm text-slate-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer Banner */}
      <section className="px-4 py-6 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <div className="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 p-5">
            <span className="mt-0.5 rounded border border-amber-500/40 bg-amber-500/20 px-1.5 py-0.5 text-xs font-bold text-amber-300">
              AVISO
            </span>
            <p className="text-sm text-amber-200 leading-relaxed">
              <span className="font-semibold">Aviso legal:</span> Esta herramienta consulta únicamente
              información disponible públicamente en portales gubernamentales. Su uso debe ser conforme
              a la{' '}
              <span className="font-medium underline underline-offset-2">
                Ley Orgánica de Protección de Datos Personales del Ecuador
              </span>
              . El uso indebido de información personal es responsabilidad exclusiva del usuario.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-800 px-4 py-6 text-center text-sm text-slate-500">
        PeopleDoxx © 2024 •{' '}
        <span className="text-slate-400">Código Abierto</span> •{' '}
        <span className="text-slate-400">MIT License</span>
      </footer>
    </div>
  );
}
