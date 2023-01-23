export class FieldError extends Error {
  constructor(public field: "email" | "password", public code: string, message?: string) {
    super(message || `${field}.${code}`);
  }
}
