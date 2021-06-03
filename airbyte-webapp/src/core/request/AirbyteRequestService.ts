import { CommonRequestError } from "core/request/CommonRequestError";
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
    let resultJsonResponse: any;

    // If some error returned in json, lets try to parse it
    try {
      resultJsonResponse = await response.json();
    } catch (e) {
      // non json result
    }

    if (resultJsonResponse?.error) {
      if (resultJsonResponse.error.startsWith("Version mismatch between")) {
        throw new VersionError(resultJsonResponse.error);
      }
    }

    throw new CommonRequestError(response, resultJsonResponse.message);
  }
}

export { AirbyteRequestService };
