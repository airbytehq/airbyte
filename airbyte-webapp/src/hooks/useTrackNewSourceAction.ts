import { useCallback } from "react";

import { useAnalyticsService } from "./services/Analytics/useAnalyticsService";

interface TrackConnectorSourceParams {
  connector_source?: string;
  connector_source_id?: string;
}

interface TrackConnectorSourceDefinitionParams {
  connector_source_definition?: string;
  connector_source_definition_id?: string;
}

type TrackNewSourceActionParams = TrackConnectorSourceParams | TrackConnectorSourceDefinitionParams;

export const useTrackNewSourceAction = () => {
  const analyticsService = useAnalyticsService();

  return useCallback(
    (action: string, params: TrackNewSourceActionParams) => {
      analyticsService.track("New Source - Action", { action, ...params });
    },
    [analyticsService]
  );
};
