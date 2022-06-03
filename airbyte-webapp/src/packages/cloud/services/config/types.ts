import * as Fullstory from "@fullstory/browser";

import { Config } from "config";

declare global {
  interface Window {
    // Cloud specific params that should be moved to cloud repo
    FULLSTORY?: string;
    FIREBASE_API_KEY?: string;
    FIREBASE_AUTH_DOMAIN?: string;
    FIREBASE_AUTH_EMULATOR_HOST?: string;
    CLOUD_API_URL?: string;
  }
}

export interface CloudConfigExtension {
  cloudApiUrl: string;
  fullstory: Fullstory.SnippetOptions & { enabled: boolean };
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
