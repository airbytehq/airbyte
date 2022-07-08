import { useCallback } from "react";

import { useAnalyticsService } from "./services/Analytics/useAnalyticsService";

export const enum LegacyTrackActionType {
  NEW_SOURCE = "New Source",
  NEW_DESTINATION = "New Destination",
  NEW_CONNECTION = "New Connection",
  SOURCE = "Source",
}

export const enum TrackActionActions {
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

export const useTrackAction = (namespace: TrackActionNamespace, legacyType?: LegacyTrackActionType) => {
  const analyticsService = useAnalyticsService();

  return useCallback(
    (
      action: string,
      actionType: TrackActionActions,
      properties: TrackConnectorActionProperties | TrackConnectionActionProperties
    ) => {
      // Calls that did not exist in the legacy format will not have a legacy event name
      const legacyEventName = legacyType ? `${legacyType} - Action)` : "";

      analyticsService.track(`Airbyte.UI.${namespace}.${actionType}`, {
        action,
        ...properties,
        legacy_event_name: legacyEventName,
      });
    },
    [analyticsService, namespace, legacyType]
  );
};
