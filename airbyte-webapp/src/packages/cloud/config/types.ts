import { Config } from "config";

export type CloudConfigExtension = {
  cloudApiUrl: string;
  firebase: {};
};

export type CloudConfig = Config & CloudConfigExtension;
