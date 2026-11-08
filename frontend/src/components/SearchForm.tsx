'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { validateCedula } from '@/lib/cedula';

export function SearchForm() {
  const router = useRouter();
  const [cedula, setCedula] = useState('');
  const [touched, setTouched] = useState(false);

  const validation = cedula.length === 10 ? validateCedula(cedula) : null;
  const showValidation = touched && cedula.length === 10;
  const isValid = validation?.valid === true;
  const canSubmit = isValid;

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, '').slice(0, 10);
    setCedula(raw);
    if (raw.length > 0) setTouched(true);
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!canSubmit) return;
      router.push(`/search?cedula=${cedula}`);
    },
    [canSubmit, cedula, router]
  );

  return (
    <form onSubmit={handleSubmit} noValidate aria-label="Formulario de búsqueda por cédula">
      <div className="relative flex flex-col gap-3 sm:flex-row">
        {/* Input */}
        <div className="relative flex-1">
          <label htmlFor="cedula-input" className="sr-only">
            Número de cédula
          </label>
          <input
            id="cedula-input"
            type="text"
            inputMode="numeric"
            pattern="\d{10}"
            maxLength={10}
            value={cedula}
            onChange={handleChange}
            placeholder="Ingrese 10 dígitos de cédula"
            autoComplete="off"
            spellCheck={false}
            aria-describedby={showValidation && !isValid ? 'cedula-error' : undefined}
            aria-invalid={showValidation && !isValid ? true : undefined}
            className={[
              'w-full rounded-xl border bg-slate-800 px-4 py-3.5 pr-12 font-mono text-lg tracking-widest text-white placeholder:font-sans placeholder:text-base placeholder:tracking-normal placeholder:text-slate-500 outline-none',
              'focus:ring-2 focus:ring-orange-500/60',
              showValidation && isValid
                ? 'border-green-500/60'
                : showValidation && !isValid
                ? 'border-red-500/60'
                : 'border-slate-600',
            ].join(' ')}
          />

          {/* Validation icon */}
          {showValidation && (
            <span
              className={[
                'pointer-events-none absolute right-3 top-1/2 -translate-y-1/2',
                isValid ? 'text-green-400' : 'text-red-400',
              ].join(' ')}
              aria-hidden="true"
            >
              {isValid ? (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </span>
          )}
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={!canSubmit}
          className="rounded-xl bg-orange-500 px-8 py-3.5 text-base font-bold text-white shadow-lg shadow-orange-500/20 hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-orange-500/60 focus:ring-offset-2 focus:ring-offset-slate-900 sm:w-auto"
          aria-label="Buscar información de la cédula ingresada"
        >
          Buscar
        </button>
      </div>

      {/* Error message */}
      {showValidation && !isValid && validation?.error && (
        <p
          id="cedula-error"
          role="alert"
          className="mt-2 text-left text-sm text-red-400"
        >
          {validation.error}
        </p>
      )}

      {/* Hint */}
      {!touched && (
        <p className="mt-2 text-center text-xs text-slate-500">
          Ejemplo: 1710034065 — Solo cédulas de ciudadanos ecuatorianos
        </p>
      )}
    </form>
  );
}
