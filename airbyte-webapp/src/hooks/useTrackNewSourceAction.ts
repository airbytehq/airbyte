import { useCallback } from "react";

import { useAnalyticsService } from "./services/Analytics/useAnalyticsService";

interface TrackNewSourceActionProperties {
  connector_source?: string;
  connector_source_id?: string;
}

export const useTrackNewSourceAction = () => {
  const analyticsService = useAnalyticsService();

  return useCallback(
    (action: string, properties: TrackNewSourceActionProperties) => {
      analyticsService.track("New Source - Action", { action, ...properties });
    },
    [analyticsService]
  );
};
