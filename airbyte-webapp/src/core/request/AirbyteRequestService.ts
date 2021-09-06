import merge from "lodash.merge";

import { CommonRequestError } from "./CommonRequestError";
import { VersionError } from "./VersionError";
import { RequestMiddleware } from "./RequestMiddleware";

abstract class AirbyteRequestService {
  constructor(
    protected rootUrl: string,
    private middlewares: RequestMiddleware[] = []
  ) {}

  /** Perform network request */
  public async fetch<T = Response>(
    url: string,
    body?: unknown,
    options?: Partial<RequestInit>
  ): Promise<T> {
    const path = `${this.rootUrl}${url}`;

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

export { AirbyteRequestService, parseResponse };
