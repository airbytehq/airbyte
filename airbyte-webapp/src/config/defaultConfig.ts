import { Feature } from "hooks/services/Feature";
import { FeatureItem } from "hooks/services/Feature/types";

import { links } from "./links";
import { Config } from "./types";

const features: Feature[] = [
  {
    id: FeatureItem.AllowUploadCustomImage,
  },
  {
    id: FeatureItem.AllowCustomDBT,
  },
  {
    id: FeatureItem.AllowUpdateConnectors,
  },
  {
    id: FeatureItem.AllowCreateConnection,
  },
  {
    id: FeatureItem.AllowSync,
  },
];

const defaultConfig: Config = {
  links,
  segment: { enabled: true, token: "" },
  healthCheckInterval: 20000,
  version: "dev",
  apiUrl: `${window.location.protocol}//${window.location.hostname}:8001/api`,
  integrationUrl: "/docs",
  oauthRedirectUrl: `${window.location.protocol}//${window.location.host}`,
  isDemo: false,
  features,
};

export { defaultConfig };
