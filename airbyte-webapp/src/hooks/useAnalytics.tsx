import React, { useContext, useMemo } from "react";
import { AnalyticsService } from "core/analytics/AnalyticsService";

const analyticsServiceContext = React.createContext<AnalyticsService | null>(
  null
);

function AnalyticsServiceProvider({
  children,
  userId,
  version,
  workspaceId,
}: {
  children: React.ReactNode;
  version?: string;
  userId?: string;
  workspaceId?: string;
}) {
  const analyticsService: AnalyticsService = useMemo(
    () =>
      new AnalyticsService(
        {
          userId,
          workspaceId,
        },
        version
      ),
    [version, userId, workspaceId]
  );
  return (
    <analyticsServiceContext.Provider value={analyticsService}>
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

  return analyticsService;
};

export default React.memo(AnalyticsServiceProvider);
