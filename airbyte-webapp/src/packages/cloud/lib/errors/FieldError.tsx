export class FieldError extends Error {
  constructor(public field: string, public code: string, message?: string) {
    super(message || `${field}.${code}`);
  }
}
