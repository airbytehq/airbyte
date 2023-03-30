import { links } from "./links";
import { Config } from "./types";

const defaultConfig: Config = {
  links,
  segment: { enabled: false, token: "" },
  healthCheckInterval: 5000,
  userDetailInterval: 5000,
  version: "dev",
  apiUrl: `http://143.198.204.26:8888/daspire`,
  integrationUrl: "/docs",
  oauthRedirectUrl: `${window.location.protocol}//${window.location.host}`,
};

export { defaultConfig };
