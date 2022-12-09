export class FormBuildError extends Error {
  __type = "form.build";
}

export function isFormBuildError(error: { __type?: string }): error is FormBuildError {
  return error.__type === "form.build";
}
