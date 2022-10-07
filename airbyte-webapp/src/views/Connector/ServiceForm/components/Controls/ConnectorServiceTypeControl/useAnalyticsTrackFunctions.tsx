import { capitalize } from "lodash";
import { useCallback } from "react";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

export const useAnalyticsTrackFunctions = (formType: "source" | "destination") => {
  const analytics = useAnalyticsService();

  const namespaceType = formType === "source" ? Namespace.SOURCE : Namespace.DESTINATION;

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
        actionDescription: `${capitalize(formType)} connector type selected`,
        [`connector_${formType}`]: connectorName,
        [`connector_${formType}_definition_id`]: connectorId,
      });
    },
    [analytics, formType, namespaceType]
  );

  return { trackMenuOpen, trackNoOptionMessage, trackConnectorSelection };
};
