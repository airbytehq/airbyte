export class NetworkError extends Error {
  status: number;
  response: Response;

  constructor(response: Response) {
    super(response.statusText);
    this.status = response.status;
    this.response = response;
  }
}
