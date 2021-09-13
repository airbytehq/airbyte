import { Config } from '@app/config';

export type CloudConfigExtension = {
  cloudApiUrl: string;
  firebase: {
    apiKey: string;
    authDomain: string;
  };
};

export type CloudConfig = Config & CloudConfigExtension;
