import { useMemo } from "react";

import { AuthService } from "./AuthService";

export function useAuthenticationService(): AuthService {
  return useMemo(() => new AuthService(process.env.REACT_APP_API_URL as string), []);
}
