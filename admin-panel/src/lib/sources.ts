export const SOURCES = ['SRI', 'SATJE', 'SUPA', 'IESS', 'CNE', 'MDT'] as const;

export type Source = (typeof SOURCES)[number];

export const SOURCE_NAMES: Record<string, string> = {
  SRI: 'Servicio de Rentas Internas',
  SATJE: 'Función Judicial',
  SUPA: 'Nómina Pública',
  IESS: 'Seguridad Social',
  CNE: 'Padrón Electoral',
  MDT: 'Ministerio del Trabajo',
};
