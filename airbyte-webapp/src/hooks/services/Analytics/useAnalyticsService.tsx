import React, { useContext, useEffect, useRef } from "react";

import { useConfig } from "config";
import { AnalyticsService } from "core/analytics/AnalyticsService";

type AnalyticsContext = Record<string, unknown>;

export const analyticsServiceContext = React.createContext<AnalyticsService | null>(null);

const AnalyticsServiceProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const { version } = useConfig();
  const analyticsService = useRef<AnalyticsService>();

  if (!analyticsService.current) {
    analyticsService.current = new AnalyticsService(version);
  }

  return (
    <analyticsServiceContext.Provider value={analyticsService.current}>{children}</analyticsServiceContext.Provider>
  );
};

export const useAnalyticsService = (): AnalyticsService => {
  const analyticsContext = useContext(analyticsServiceContext);

  if (!analyticsContext) {
    throw new Error("analyticsContext must be used within a AnalyticsServiceProvider.");
  }

  return analyticsContext;
};

export const useAnalyticsIdentifyUser = (userId?: string, traits?: Record<string, unknown>): void => {
  const analyticsService = useAnalyticsService();

  useEffect(() => {
    if (userId) {
      analyticsService.identify(userId, traits);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);
};

export const useTrackPage = (page: string): void => {
  const analyticsService = useAnalyticsService();

  useEffect(() => {
    analyticsService.page(page);
  }, [analyticsService, page]);
};

export const useAnalyticsRegisterValues = (props?: AnalyticsContext | null): void => {
  const service = useAnalyticsService();

  useEffect(() => {
    if (!props) {
      return;
    }

    service.setContext(props);
    return () => service.removeFromContext(...Object.keys(props));

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props]);
};

export default React.memo(AnalyticsServiceProvider);
