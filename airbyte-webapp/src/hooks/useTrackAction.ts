import { useCallback } from "react";

import { useAnalyticsService } from "./services/Analytics/useAnalyticsService";

export const enum TrackActionLegacyType {
  NEW_SOURCE = "New Source",
  NEW_DESTINATION = "New Destination",
  NEW_CONNECTION = "New Connection",
  SOURCE = "Source",
}

export const enum TrackActionType {
  CREATE = "Create",
  TEST = "Test",
  SELECT = "Select",
  SUCCESS = "TestSuccess",
  FAILURE = "TestFailure",
  FREQUENCY = "FrequencySet",
  SYNC = "FullRefreshSync",
  SCHEMA = "EditSchema",
  DISABLE = "Disable",
  REENABLE = "Reenable",
  DELETE = "Delete",
}

export const enum TrackActionNamespace {
  SOURCE = "Source",
  DESTINATION = "Destination",
  CONNECTION = "Connection",
}

interface TrackConnectorActionProperties {
  connector_source?: string;
  connector_source_definition_id?: string;
  connector_destination?: string;
  connector_destination_definition_id?: string;
}

interface TrackConnectionActionProperties {
  frequency: string;
  connector_source_definition: string;
  connector_source_definition_id: string;
  connector_destination_definition: string;
  connector_destination_definition_id: string;
  available_streams: number;
  enabled_streams: number;
}

export const useTrackAction = (namespace: TrackActionNamespace, legacyType?: TrackActionLegacyType) => {
  const analyticsService = useAnalyticsService();

  return useCallback(
    (
      actionDescription: string,
      actionType: TrackActionType,
      properties: TrackConnectorActionProperties | TrackConnectionActionProperties
    ) => {
      // Calls that did not exist in the legacy format will not have a legacy event name
      const legacyEventName = legacyType ? `${legacyType} - Action` : "";

      analyticsService.track(`Airbyte.UI.${namespace}.${actionType}`, {
        actionDescription,
        ...properties,
        legacy_event_name: legacyEventName,
      });
    },
    [analyticsService, namespace, legacyType]
  );
};
