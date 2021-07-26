import React, { useEffect } from "react";
import * as FullStory from "@fullstory/browser";

import config from "config";
import useFullStory from "components/hooks/useFullStory";
import AnalyticsServiceProvider, {
  useAnalytics,
} from "components/hooks/useAnalytics";
import useTracker from "components/hooks/useOpenReplay";
import { useCurrentWorkspace } from "components/hooks/services/useWorkspace";

function WithAnalytics({
  customerId,
}: {
  customerId: string;
  workspaceId?: string;
}) {
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

const AnalyticsInitializer: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const workspace = useCurrentWorkspace();

  return (
    <AnalyticsServiceProvider
      userId={workspace.workspaceId}
      version={config.version}
    >
      <WithAnalytics customerId={workspace.customerId} />
      {children}
    </AnalyticsServiceProvider>
  );
};

export { AnalyticsInitializer };
