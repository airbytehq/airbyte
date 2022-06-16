import { useCallback } from "react";

import { useAnalyticsService } from "./services/Analytics/useAnalyticsService";

export const enum LegacyTrackActionType {
  NEW_SOURCE = "New Source",
  NEW_DESTINATION = "New Destination",
}

export const enum TrackActionActions {
  CREATE = "Create",
  TEST = "Test",
  SELECT = "Select",
  SUCCESS = "Success",
  FAILURE = "Failure",
}

export const enum TrackActionNamespace {
  SOURCE = "Source",
  DESTINATION = "Destination",
}

interface TrackActionProperties {
  connector_source?: string;
  connector_source_definition_id?: string;
  connector_destination?: string;
  connector_destination_definition_id?: string;
}

export const useTrackAction = (namespace: TrackActionNamespace, type: LegacyTrackActionType) => {
  const analyticsService = useAnalyticsService();

  return useCallback(
    (action: string, actionTypes: TrackActionActions[], properties: TrackActionProperties) => {
      const actionTypesString = actionTypes.toString().replaceAll(",", ".");

      analyticsService.track(`Airbyte.UI.${namespace}.${actionTypesString}`, {
        action,
        ...properties,
        legacy_event_name: `${type} - Action`,
      });
    },
    [analyticsService, namespace, type]
  );
};
