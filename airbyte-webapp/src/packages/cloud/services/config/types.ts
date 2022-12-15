import { Config } from "config";

declare global {
  interface Window {
    // Cloud specific params that should be moved to cloud repo
    FIREBASE_API_KEY?: string;
    FIREBASE_AUTH_DOMAIN?: string;
    FIREBASE_AUTH_EMULATOR_HOST?: string;
    CLOUD_API_URL?: string;
    CLOUD_PUBLIC_API_URL?: string;
  }
}

export interface CloudConfigExtension {
  cloudApiUrl: string;
  cloudPublicApiUrl: string;
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
