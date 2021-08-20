export class CommonRequestError extends Error {
  __type = "common.error";
  response: Response;
  // TODO: Add better error hierarchy
  _status?: number;

  constructor(response: Response, msg?: string) {
    super(response.statusText);
    this.response = response;
    this.message = msg ?? "common.error";
  }

  get status(): number {
    return this._status || this.response.status;
  }
}

export function isCommonRequestError(error: any): error is CommonRequestError {
  return error.__type === "common.error";
}
