export class CommonRequestError extends Error {
  __type = "common.error";
  // TODO: Add better error hierarchy
  _status?: number;

  constructor(protected response: Response | undefined, msg?: string) {
    super(response?.statusText);
    this.response = response;
    this.message = msg ?? "common.error";
  }

  get status(): number {
    return (this._status || this.response?.status) ?? 400;
  }
}

export function isCommonRequestError(error: { __type?: string }): error is CommonRequestError {
  return error.__type === "common.error";
}
