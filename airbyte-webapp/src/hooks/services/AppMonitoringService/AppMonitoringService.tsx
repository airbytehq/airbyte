import { datadogRum } from "@datadog/browser-rum";
import React, { createContext, useContext } from "react";

const appMonitoringContext = createContext<AppMonitoringServiceProviderValue | null>(null);

/**
 * The AppMonitoringService exposes methods for tracking actions and errors from the webapp.
 * These methods are particularly useful for tracking when unexpected or edge-case conditions
 * are encountered in production.
 */
interface AppMonitoringServiceProviderValue {
  trackAction: (actionName: string, context?: Record<string, unknown>) => void;
  trackError: (error: Error, context?: Record<string, unknown>) => void;
}

export const useAppMonitoringService = (): AppMonitoringServiceProviderValue => {
  const context = useContext(appMonitoringContext);
  if (context === null) {
    throw new Error("useAppMonitoringService must be used within a AppMonitoringServiceProvider");
  }

  return context;
};

/**
 * This implementation of the AppMonitoringService uses the datadog SDK to track errors and actions
 */
export const AppMonitoringServiceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const trackAction = (action: string, context?: Record<string, unknown>) => {
    datadogRum.addAction(action, context);
  };

  const trackError = (error: Error, context?: Record<string, unknown>) => {
    datadogRum.addError(error, context);
  };

  return <appMonitoringContext.Provider value={{ trackAction, trackError }}>{children}</appMonitoringContext.Provider>;
};
