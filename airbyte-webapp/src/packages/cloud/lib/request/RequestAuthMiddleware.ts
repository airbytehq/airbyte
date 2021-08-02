import merge from "lodash.merge";

interface JwtProvider {
  getValue(): string;
}

export function RequestAuthMiddleware(
  jwtProvider: JwtProvider
): (options: RequestInit) => RequestInit {
  return (options: RequestInit) => ({
    ...options,
    header: merge(options.headers, {
      Authorization: `Bearer ${jwtProvider.getValue()}`,
    }),
  });
}
