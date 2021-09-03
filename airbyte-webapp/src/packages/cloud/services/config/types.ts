import { Config } from "config";

export type CloudConfigExtension = {
  cloudApiUrl: string;
  firebase: {
    apiKey: string;
    authDomain: string;
  };
};

export type CloudConfig = Config & CloudConfigExtension;
