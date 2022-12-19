export class FormBuildError extends Error {
  __type = "form.build";

  constructor(public message: string, public connectorId?: string) {
    super(message);
  }
}

export function isFormBuildError(error: { __type?: string }): error is FormBuildError {
  return error.__type === "form.build";
}
