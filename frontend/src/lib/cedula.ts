export interface CedulaValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * Validates an Ecuadorian cédula using the Módulo 10 check digit algorithm.
 *
 * Rules:
 * - Must be exactly 10 digits
 * - Digits 1-2 (province code) must be 01-24 or 30 (special: Ecuadorians abroad)
 * - Third digit must be < 6 (natural persons)
 * - Luhn-like checksum using coefficients [2,1,2,1,2,1,2,1,2]
 */
export function validateCedula(cedula: string): CedulaValidationResult {
  const trimmed = cedula.trim();

  if (!/^\d+$/.test(trimmed)) {
    return { valid: false, error: 'La cédula debe contener únicamente dígitos.' };
  }

  if (trimmed.length !== 10) {
    return { valid: false, error: 'La cédula debe tener exactamente 10 dígitos.' };
  }

  const digits = trimmed.split('').map(Number);

  // Province code: first two digits, 01-24 or 30
  const province = digits[0] * 10 + digits[1];
  const validProvinces =
    (province >= 1 && province <= 24) || province === 30;

  if (!validProvinces) {
    return {
      valid: false,
      error: `Código de provincia inválido (${String(province).padStart(2, '0')}). Debe ser 01-24 o 30.`,
    };
  }

  // Third digit must be < 6 for natural persons
  if (digits[2] >= 6) {
    return {
      valid: false,
      error: 'El tercer dígito debe ser menor a 6 para personas naturales.',
    };
  }

  // Módulo 10 checksum
  const coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2];
  let sum = 0;

  for (let i = 0; i < 9; i++) {
    let product = digits[i] * coefficients[i];
    if (product > 9) {
      product -= 9;
    }
    sum += product;
  }

  const remainder = sum % 10;
  const checkDigit = remainder === 0 ? 0 : 10 - remainder;

  if (checkDigit !== digits[9]) {
    return { valid: false, error: 'El dígito verificador es incorrecto.' };
  }

  return { valid: true };
}
