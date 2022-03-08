import { Config } from "./types";
import { uiConfig } from "./uiConfig";
import { Feature } from "hooks/services/Feature";
import { FeatureItem } from "hooks/services/Feature/types";

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
];

const defaultConfig: Config = {
  ui: uiConfig,
  segment: { enabled: true, token: "" },
  healthCheckInterval: 20000,
  version: "dev",
  apiUrl: `http://ec2-52-91-211-217.compute-1.amazonaws.com:8000/api/v1/`,
  integrationUrl: "/docs",
  oauthRedirectUrl: `${window.location.protocol}//${window.location.host}`,
  isDemo: false,
  features,
};

export { defaultConfig };
