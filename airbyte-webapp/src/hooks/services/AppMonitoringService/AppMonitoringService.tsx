import { datadogRum } from "@datadog/browser-rum";
import React, { createContext, useContext } from "react";

import { AppActionCodes } from "./actionCodes";

const appMonitoringContext = createContext<AppMonitoringServiceProviderValue | null>(null);

export type TrackActionFn = (actionCode: AppActionCodes, context?: Record<string, unknown>) => void;
export type TrackErrorFn = (error: Error, context?: Record<string, unknown>) => void;

/**
 * The AppMonitoringService exposes methods for tracking actions and errors from the webapp.
 * These methods are particularly useful for tracking when unexpected or edge-case conditions
 * are encountered in production.
 */
interface AppMonitoringServiceProviderValue {
  /**
   * Log a custom action in datadog. Useful for tracking edge cases or unexpected application states.
   */
  trackAction: TrackActionFn;
  /**
   * Log a custom error in datadog. Useful for tracking edge case errors while handling them in the UI.
   */
  trackError: TrackErrorFn;
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
export const AppMonitoringServiceProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  const trackAction = (action: string, context?: Record<string, unknown>) => {
    if (!datadogRum.getInternalContext()) {
      console.debug(`trackAction(${action}) failed because RUM is not initialized.`);
      return;
    }

    datadogRum.addAction(action, context);
  };

  const trackError = (error: Error, context?: Record<string, unknown>) => {
    if (!datadogRum.getInternalContext()) {
      console.debug(`trackError() failed because RUM is not initialized. \n`, error);
      return;
    }

    datadogRum.addError(error, context);
  };

  return <appMonitoringContext.Provider value={{ trackAction, trackError }}>{children}</appMonitoringContext.Provider>;
};
