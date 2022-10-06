import { Config } from "config";

declare global {
  interface Window {
    // Cloud specific params that should be moved to cloud repo
    FIREBASE_API_KEY?: string;
    FIREBASE_AUTH_DOMAIN?: string;
    FIREBASE_AUTH_EMULATOR_HOST?: string;
    CLOUD_API_URL?: string;
  }
}

export interface CloudConfigExtension {
  cloudApiUrl: string;
  datadog: {
    applicationId: string;
    clientToken: string;
    site: string;
    service: string;
  };
  firebase: {
    apiKey: string;
    authDomain: string;
    authEmulatorHost: string;
  };
  intercom: {
    appId: string;
  };
}

export type CloudConfig = Config & CloudConfigExtension;
