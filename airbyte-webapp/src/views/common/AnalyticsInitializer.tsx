import React, { useEffect } from "react";
import * as FullStory from "@fullstory/browser";

import config from "config";
import useFullStory from "hooks/useFullStory";
import AnalyticsServiceProvider, { useAnalytics } from "hooks/useAnalytics";
import useTracker from "hooks/useOpenReplay";
import useSegment from "hooks/useSegment";

function WithAnalytics({
  customerId,
}: {
  customerId: string;
  workspaceId?: string;
}) {
  useSegment(config.segment.enabled ? config.segment.token : "");
  const analyticsService = useAnalytics();

  useEffect(() => {
    analyticsService.identify(customerId);
  }, [analyticsService, customerId]);

  const tracker = useTracker(config.openreplay);
  useEffect(() => {
    tracker.userID(customerId);
  }, [tracker, customerId]);

  const initializedFullstory = useFullStory(config.fullstory);
  useEffect(() => {
    if (initializedFullstory) {
      FullStory.identify(customerId);
    }
  }, [initializedFullstory, customerId]);

  return null;
}

const AnalyticsInitializer: React.FC<{
  children: React.ReactNode;
  customerIdProvider: () => string;
}> = ({ children, customerIdProvider }) => {
  const customerId = customerIdProvider();

  return (
    <AnalyticsServiceProvider userId={customerId} version={config.version}>
      <WithAnalytics customerId={customerId} />
      {children}
    </AnalyticsServiceProvider>
  );
};

export { AnalyticsInitializer };
