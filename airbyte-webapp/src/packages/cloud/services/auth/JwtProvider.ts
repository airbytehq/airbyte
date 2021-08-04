import { JwtProvider } from "packages/cloud/lib/auth/RequestAuthMiddleware";
import { token } from "./AuthService";

const jwtProvider: JwtProvider = {
  getValue: (): string => token,
};

export { jwtProvider };
