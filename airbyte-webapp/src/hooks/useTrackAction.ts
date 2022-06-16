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
  SUCCESS = "Success",
  FAILURE = "Failure",
  FREQUENCY = "Frequency",
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
  frequency?: string; //todo: i don't like this here... but the disable/reenable call in the EntityTable hooks sends it with the other data for this type of call?  get clarification on what data should be sent with what calls...
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

export const useTrackAction = (namespace: TrackActionNamespace, type: LegacyTrackActionType) => {
  const analyticsService = useAnalyticsService();

  return useCallback(
    (
      action: string,
      actionTypes: TrackActionActions[],
      properties: TrackConnectorActionProperties | TrackConnectionActionProperties
    ) => {
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
