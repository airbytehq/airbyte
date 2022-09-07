import React, { useContext, useEffect, useMemo } from "react";
import { useMap } from "react-use";

import { AnalyticsService } from "core/analytics/AnalyticsService";

type AnalyticsContext = Record<string, unknown>;

export interface AnalyticsServiceProviderValue {
  analyticsContext: AnalyticsContext;
  setContext: (ctx: AnalyticsContext) => void;
  addContextProps: (props: AnalyticsContext) => void;
  removeContextProps: (props: string[]) => void;
  service: AnalyticsService;
}

export const analyticsServiceContext = React.createContext<AnalyticsServiceProviderValue | null>(null);

const AnalyticsServiceProvider = ({
  children,
  version,
  initialContext = {},
}: {
  children: React.ReactNode;
  version?: string;
  initialContext?: AnalyticsContext;
}) => {
  const [analyticsContext, { set, setAll, remove }] = useMap(initialContext);

  const analyticsService: AnalyticsService = useMemo(
    () => new AnalyticsService(analyticsContext, version),
    [version, analyticsContext]
  );

  const handleAddContextProps = (props: AnalyticsContext) => {
    Object.entries(props).forEach((value) => set(...value));
  };

  const handleRemoveContextProps = (props: string[]) => props.forEach(remove);

  return (
    <analyticsServiceContext.Provider
      value={{
        analyticsContext,
        setContext: setAll,
        addContextProps: handleAddContextProps,
        removeContextProps: handleRemoveContextProps,
        service: analyticsService,
      }}
    >
      {children}
    </analyticsServiceContext.Provider>
  );
};

export const useAnalyticsService = (): AnalyticsService => {
  return useAnalytics().service;
};

export const useAnalytics = (): AnalyticsServiceProviderValue => {
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
  const { addContextProps, removeContextProps } = useAnalytics();

  useEffect(() => {
    if (!props) {
      return;
    }

    addContextProps(props);
    return () => removeContextProps(Object.keys(props));

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props]);
};

export default React.memo(AnalyticsServiceProvider);
