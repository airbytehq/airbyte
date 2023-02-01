import { useCallback } from "react";

import { Action, Namespace } from "core/analytics";
import { Connector, ConnectorDefinition } from "core/domain/connector";
import { useAnalyticsService } from "hooks/services/Analytics";

export const useAnalyticsTrackFunctions = (connectorType: "source" | "destination") => {
  const analytics = useAnalyticsService();

  const namespaceType = connectorType === "source" ? Namespace.SOURCE : Namespace.DESTINATION;

  const trackAction = useCallback(
    (connector: ConnectorDefinition | undefined, actionType: Action, actionDescription: string) => {
      if (!connector) {
        return;
      }
      analytics.track(namespaceType, actionType, {
        actionDescription,
        connector: connector.name,
        connector_definition_id: Connector.id(connector),
        connector_documentation_url: connector.documentationUrl,
      });
    },
    [analytics, namespaceType]
  );

  const trackTestConnectorStarted = useCallback(
    (connector: ConnectorDefinition | undefined) => {
      trackAction(connector, Action.TEST, "Test a connector");
    },
    [trackAction]
  );

  const trackTestConnectorSuccess = useCallback(
    (connector: ConnectorDefinition | undefined) => {
      trackAction(connector, Action.SUCCESS, "Tested connector - success");
    },
    [trackAction]
  );

  const trackTestConnectorFailure = useCallback(
    (connector: ConnectorDefinition | undefined) => {
      trackAction(connector, Action.FAILURE, "Tested connector - failure");
    },
    [trackAction]
  );
  return { trackTestConnectorStarted, trackTestConnectorSuccess, trackTestConnectorFailure };
};
