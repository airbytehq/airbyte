import React from "react";
import { IntercomProvider as IntercomProviderCore } from "react-use-intercom";
import { useConfig } from "packages/cloud/services/config";

const IntercomProvider: React.FC = ({ children }) => {
  const config = useConfig();

  return (
    <IntercomProviderCore appId={config.intercom.appId}>
      {children}
    </IntercomProviderCore>
  );
};

export { IntercomProvider };
