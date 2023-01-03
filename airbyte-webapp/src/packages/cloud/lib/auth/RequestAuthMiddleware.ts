import merge from "lodash/merge";

import { RequestMiddleware } from "core/request/RequestMiddleware";

export interface JwtProvider {
  getValue(): string | Promise<string>;
}

export function RequestAuthMiddleware(jwtProvider: JwtProvider): RequestMiddleware {
  return async (options: RequestInit) => ({
    ...options,
    headers: merge(options.headers, {
      Authorization: `Bearer ${await jwtProvider.getValue()}`,
    }),
  });
}
