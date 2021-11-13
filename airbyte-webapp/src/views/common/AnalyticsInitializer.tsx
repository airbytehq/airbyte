import React, { useEffect } from "react";

import { useConfig } from "config";
import AnalyticsServiceProvider, {
  useAnalyticsService,
} from "hooks/services/Analytics/useAnalyticsService";
import useSegment from "hooks/useSegment";
import { useGetService } from "core/servicesProvider";

const InitialIdentify: React.FC<{ customerId: string }> = ({
  customerId,
}: {
  customerId: string;
}) => {
  const config = useConfig();

  // segment section
  useSegment(config.segment.enabled ? config.segment.token : "");
  const analyticsService = useAnalyticsService();

  useEffect(() => analyticsService.identify(customerId), [
    analyticsService,
    customerId,
  ]);

  return null;
};

const AnalyticsInitializer: React.FC = ({ children }) => {
  const customerIdProvider = useGetService<() => string>(
    "useCustomerIdProvider"
  );

  const userId = customerIdProvider();
  const config = useConfig();

  return (
    <AnalyticsServiceProvider
      initialContext={{ userId }}
      version={config.version}
    >
      <InitialIdentify customerId={userId} />
      {children}
    </AnalyticsServiceProvider>
  );
};

export { AnalyticsInitializer };
