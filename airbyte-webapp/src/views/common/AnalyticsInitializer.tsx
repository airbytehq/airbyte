import React from "react";
import useSegment from "components/hooks/useSegment";
import config from "config";
import useFullStory from "components/hooks/useFullStory";
import AnalyticsServiceProvider from "components/hooks/useAnalytics";
import useOpenReplay from "components/hooks/useOpenReplay";
import useWorkspace from "components/hooks/services/useWorkspace";

const AnalyticsInitializer: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  useSegment(config.segment.token);
  useFullStory(config.fullstory);
  useOpenReplay(config.openreplay.projectKey);

  const { workspace } = useWorkspace();
  return (
    <AnalyticsServiceProvider
      userId={workspace.workspaceId}
      version={config.version}
    >
      {children}
    </AnalyticsServiceProvider>
  );
};

export { AnalyticsInitializer };
