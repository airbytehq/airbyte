import merge from "lodash/merge";

import { ApiOverrideRequestOptions } from "./apiOverride";
import { CommonRequestError } from "./CommonRequestError";
import { RequestMiddleware } from "./RequestMiddleware";
import { VersionError } from "./VersionError";

abstract class AirbyteRequestService {
  private readonly rootUrl: string;

  constructor(rootUrl: string, private middlewares: RequestMiddleware[] = []) {
    // Remove the `/v1/` at the end of the URL if it exists, during the transition period
    // to remove it from all cloud environments
    this.rootUrl = rootUrl.replace(/\/v1\/?$/, "");
  }

  protected get requestOptions(): ApiOverrideRequestOptions {
    return {
      config: { apiUrl: this.rootUrl },
      middlewares: this.middlewares,
    };
  }

  /** Perform network request */
  public async fetch<T = Response>(url: string, body?: unknown, options?: Partial<RequestInit>): Promise<T> {
    const path = `${this.rootUrl}${url.startsWith("/") ? "" : "/"}${url}`;

    const requestOptions: RequestInit = merge(
      {
        method: "POST",
        body: body ? JSON.stringify(body) : undefined,
        headers: {
          "Content-Type": "application/json",
        },
      },
      options
    );

    let preparedOptions: RequestInit = requestOptions;

    for (const middleware of this.middlewares) {
      preparedOptions = await middleware(preparedOptions);
    }
    const response = await fetch(path, preparedOptions);

    return parseResponse(response);
  }
}

/** Parses errors from server */
async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return {} as T;
  }
  if (response.status >= 200 && response.status < 300) {
    const contentType = response.headers.get("content-type");

    if (contentType === "application/json") {
      return await response.json();
    }

    // @ts-expect-error TODO: needs refactoring of services
    return response;
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

export { AirbyteRequestService };
