import React, { useContext, useMemo, useState } from "react";
import { AnalyticsService } from "core/analytics/AnalyticsService";

export type AnalyticsServiceProviderValue = {
  setContext: (ctx: Record<string, unknown>) => void;
  service: AnalyticsService;
};

const analyticsServiceContext = React.createContext<AnalyticsServiceProviderValue | null>(
  null
);

function AnalyticsServiceProvider<T extends Record<string, unknown>>({
  children,
  version,
  context = {} as T,
}: {
  children: React.ReactNode;
  version?: string;
  context?: T;
}) {
  const [ctx, setCtx] = useState<T>(context);

  const analyticsService: AnalyticsService = useMemo(
    () => new AnalyticsService(ctx, version),
    [version, ctx]
  );

  return (
    <analyticsServiceContext.Provider
      value={{
        setContext: (c) => setCtx(c as T),
        service: analyticsService,
      }}
    >
      {children}
    </analyticsServiceContext.Provider>
  );
}

export const useAnalytics = (): AnalyticsService => {
  const analyticsService = useContext(analyticsServiceContext);

  if (!analyticsService) {
    throw new Error(
      "analyticsService must be used within a AnalyticsServiceProvider."
    );
  }

  return analyticsService.service;
};

export const useAnalyticsCtx = (): AnalyticsServiceProviderValue => {
  const analyticsService = useContext(analyticsServiceContext);

  if (!analyticsService) {
    throw new Error(
      "analyticsService must be used within a AnalyticsServiceProvider."
    );
  }

  return analyticsService;
};

export default React.memo(AnalyticsServiceProvider);
