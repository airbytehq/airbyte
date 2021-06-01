export class CommonRequestError extends Error {
  response: Response;

  constructor(response: Response, msg?: string) {
    super(response.statusText);
    this.response = response;
    this.message = msg ?? "common.error";
  }

  get status(): number {
    return this.response.status;
  }
}
