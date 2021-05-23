import { NetworkError } from "core/request/NetworkError";
import config from "config";
import { VersionError } from "./VersionError";

abstract class AirbyteRequestService {
  static rootUrl = config.apiUrl;

  /** Perform network request */
  static async fetch(
    url: string,
    body?: Readonly<Record<string, unknown> | Array<unknown> | string>,
    options?: Partial<RequestInit>
  ): Promise<Response> {
    const path = `${this.rootUrl}${url}`;
    const response = await fetch(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    });

    return this.parseResponse(response);
  }

  /** Parses errors from server */
  static async parseResponse<T>(response: Response): Promise<T> {
    if (response.status === 204) {
      return {} as T;
    }
    if (response.status >= 200 && response.status < 300) {
      return response.status === 204 ? {} : await response.json();
    }
    let result: any;

    // If some error returned in json, lets try to parse it
    try {
      result = await response.json();
    } catch (e) {
      //
    }

    if (result?.error) {
      if (result.error.startsWith("Version mismatch between")) {
        throw new VersionError(result.error);
      }
    }

    const e = new NetworkError(response);
    e.status = response.status;
    e.message = result.message;
    throw e;
  }
}

export { AirbyteRequestService };
