export class CommonRequestError extends Error {
  status: number;
  response: Response;

  constructor(response: Response, msg?: string) {
    super(response.statusText);
    this.status = response.status;
    this.response = response;
    this.message = msg ?? "common.error";
  }
}
