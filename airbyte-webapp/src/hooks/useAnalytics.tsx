import React, { useContext, useMemo, useState } from "react";
import { AnalyticsService } from "core/analytics/AnalyticsService";

export type AnalyticsServiceProviderValue = {
  setContext: (ctx: Record<string, unknown>) => void;
  addContextProps: (props: Record<string, unknown>) => void;
  removeContextProps: (props: string[]) => void;
  service: AnalyticsService;
};

const analyticsServiceContext = React.createContext<AnalyticsServiceProviderValue | null>(
  null
);

function AnalyticsServiceProvider({
  children,
  version,
  context,
}: {
  children: React.ReactNode;
  version?: string;
  context?: Record<string, unknown>;
}) {
  const [ctx, setCtx] = useState<Record<string, unknown>>(context || {});

  const analyticsService: AnalyticsService = useMemo(
    () => new AnalyticsService(ctx, version),
    [version, ctx]
  );

  const handleAddContextProps = (props: Record<string, unknown>) => {
    return {
      ...ctx,
      ...props,
    };
  };

  const handleRemoveContextProps = (props: string[]) => {
    const newCtx = Object.keys(ctx).reduce((result, key) => {
      if (props.includes(key)) {
        return result;
      }

      return {
        [key]: ctx[key],
        ...result,
      };
    }, {});

    setCtx(newCtx);
  };

  return (
    <analyticsServiceContext.Provider
      value={{
        setContext: setCtx,
        addContextProps: handleAddContextProps,
        removeContextProps: handleRemoveContextProps,
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
