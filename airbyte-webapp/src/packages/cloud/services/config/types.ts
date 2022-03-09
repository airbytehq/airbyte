import { Config } from "config";
import * as Fullstory from "@fullstory/browser";

declare global {
  interface Window {
    // Cloud specific params that should be moved to cloud repo
    FULLSTORY?: string;
    FIREBASE_API_KEY?: string;
    FIREBASE_AUTH_DOMAIN?: string;
    CLOUD_API_URL?: string;
  }
}

export type CloudConfigExtension = {
  cloudApiUrl: string;
  fullstory: Fullstory.SnippetOptions & { enabled: boolean };
  firebase: {
    apiKey: string;
    authDomain: string;
  };
  intercom: {
    appId: string;
  };
};

export type CloudConfig = Config & CloudConfigExtension;
