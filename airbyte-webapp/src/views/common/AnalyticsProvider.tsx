import React from "react";

import { useConfig } from "config";
import AnalyticsServiceProvider from "hooks/services/Analytics/useAnalyticsService";
import useSegment from "hooks/useSegment";

const AnalyticsProvider: React.FC = ({ children }) => {
  const config = useConfig();
  useSegment(config.segment.enabled ? config.segment.token : "");

  return <AnalyticsServiceProvider version={config.version}>{children}</AnalyticsServiceProvider>;
};

export { AnalyticsProvider };
