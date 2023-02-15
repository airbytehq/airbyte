import React from "react";
import { IntercomProvider as IntercomProviderCore } from "react-use-intercom";

import { MissingConfigError, useConfig } from "config";

const IntercomProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { intercom } = useConfig();

  if (!intercom.appId) {
    throw new MissingConfigError("Missing required configuration intercom.appId");
  }
  return <IntercomProviderCore appId={intercom.appId}>{children}</IntercomProviderCore>;
};

export { IntercomProvider };
