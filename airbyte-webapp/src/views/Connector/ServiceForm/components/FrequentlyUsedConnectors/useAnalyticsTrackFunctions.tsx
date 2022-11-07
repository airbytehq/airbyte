import { useCallback } from "react";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

export const useAnalyticsTrackFunctions = (connectorType: "source" | "destination") => {
  const analytics = useAnalyticsService();

  const namespaceType = connectorType === "source" ? Namespace.SOURCE : Namespace.DESTINATION;

  const trackSelectedSuggestedConnector = useCallback(
    (connectorId: string, connectorName: string) => {
      analytics.track(namespaceType, Action.SELECT, {
        actionDescription: "Suggested connector type selected",
        [`connector_${connectorType}`]: connectorName,
        [`connector_${connectorType}_definition_id`]: connectorId,
        [`connector_${connectorType}_suggested`]: true,
      });
    },
    [analytics]
  );
  return { trackSelectedSuggestedConnector };
};
