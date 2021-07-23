import config from "config";

import { CommonRequestError } from "core/request/CommonRequestError";
import { VersionError } from "./VersionError";

abstract class AirbyteRequestService {
  static rootUrl = config.apiUrl;

  fetch(
    url: string,
    body?: unknown,
    options?: Partial<RequestInit>
  ): Promise<Response> {
    return AirbyteRequestService.fetch(url, body, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers ?? {}),
      },
    });
  }
  /** Perform network request */
  static async fetch(
    url: string,
    body?: unknown,
    options?: Partial<RequestInit>
  ): Promise<Response> {
    const path = `${this.rootUrl}${url}`;
    const response = await fetch(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
      ...options,
    });

    return AirbyteRequestService.parseResponse(response);
  }

  /** Parses errors from server */
  static async parseResponse<T>(response: Response): Promise<T> {
    if (response.status === 204) {
      return {} as T;
    }
    if (response.status >= 200 && response.status < 300) {
      const contentType = response.headers.get("content-type");

      if (contentType === "application/json") {
        return await response.json();
      }

      // @ts-ignore needs refactoring of services
      // TODO: refactor
      return response;
    }
    let resultJsonResponse: any;

    // If some error returned in json, lets try to parse it
    try {
      resultJsonResponse = await response.json();
    } catch (e) {
      // non json result
      throw new CommonRequestError(response, "non-json response");
    }

    if (resultJsonResponse?.error) {
      if (resultJsonResponse.error.startsWith("Version mismatch between")) {
        throw new VersionError(resultJsonResponse.error);
      }
    }

    throw new CommonRequestError(response, resultJsonResponse?.message);
  }
}

export { AirbyteRequestService };
