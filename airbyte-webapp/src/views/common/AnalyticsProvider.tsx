import React from "react";

import { useConfig } from "config";
import AnalyticsServiceProvider from "hooks/services/Analytics/useAnalyticsService";
import useSegment from "hooks/useSegment";

export const AnalyticsProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const config = useConfig();
  useSegment(config.segment.enabled ? config.segment.token : "");

  return <AnalyticsServiceProvider>{children}</AnalyticsServiceProvider>;
};
