import { NetworkError } from "core/request/NetworkError";
import config from "config";

abstract class AirbyteRequestService {
  static rootUrl = config.apiUrl;

  /** Perform network request*/
  static async fetch(
    url: string,
    body?: Readonly<Record<string, unknown> | Array<unknown> | string>,
    options?: Partial<RequestInit>
  ): Promise<Response> {
    const response = await fetch(url, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    });

    if (response.status >= 200 && response.status < 300) {
      return response;
    } else {
      const e = new NetworkError(response);
      e.status = response.status;
      throw e;
    }
  }
}

export { AirbyteRequestService };
