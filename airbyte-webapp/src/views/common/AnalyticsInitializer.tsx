import React, { useEffect } from "react";

import { useConfig } from "config";
import AnalyticsServiceProvider, { useAnalytics } from "hooks/useAnalytics";
import useSegment from "hooks/useSegment";
import { useGetService } from "core/servicesProvider";

function WithAnalytics({
  customerId,
}: {
  customerId: string;
  workspaceId?: string;
}) {
  const config = useConfig();

  // segment section
  useSegment(config.segment.enabled ? config.segment.token : "");
  const analyticsService = useAnalytics();
  useEffect(() => {
    analyticsService.identify(customerId);
  }, [analyticsService, customerId]);

  return null;
}

const AnalyticsInitializer: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const customerIdProvider = useGetService<() => string>(
    "useCustomerIdProvider"
  );
  const customerId = customerIdProvider();
  const config = useConfig();

  return (
    <AnalyticsServiceProvider userId={customerId} version={config.version}>
      <WithAnalytics customerId={customerId} />
      {children}
    </AnalyticsServiceProvider>
  );
};

export { AnalyticsInitializer };
