import capitalize from "lodash/capitalize";
import { useCallback } from "react";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

export const useAnalyticsTrackFunctions = (connectorType: "source" | "destination") => {
  const analytics = useAnalyticsService();

  const namespaceType = connectorType === "source" ? Namespace.SOURCE : Namespace.DESTINATION;

  const trackMenuOpen = useCallback(() => {
    analytics.track(namespaceType, Action.SELECTION_OPENED, {
      actionDescription: "Opened connector type selection",
    });
  }, [analytics, namespaceType]);

  const trackNoOptionMessage = useCallback(
    (inputValue: string) => {
      analytics.track(namespaceType, Action.NO_MATCHING_CONNECTOR, {
        actionDescription: "Connector query without results",
        query: inputValue,
      });
    },
    [analytics, namespaceType]
  );

  const trackConnectorSelection = useCallback(
    (connectorId: string, connectorName: string) => {
      analytics.track(namespaceType, Action.SELECT, {
        actionDescription: `${capitalize(connectorType)} connector type selected`,
        [`connector_${connectorType}`]: connectorName,
        [`connector_${connectorType}_definition_id`]: connectorId,
      });
    },
    [analytics, connectorType, namespaceType]
  );

  return { trackMenuOpen, trackNoOptionMessage, trackConnectorSelection };
};
