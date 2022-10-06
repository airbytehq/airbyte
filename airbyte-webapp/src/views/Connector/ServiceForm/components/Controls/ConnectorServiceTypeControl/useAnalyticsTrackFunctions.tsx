import { capitalize } from "lodash";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

export const useAnalyticsTrackFunctions = (formType: "source" | "destination") => {
  const analytics = useAnalyticsService();

  const namespaceType = formType === "source" ? Namespace.SOURCE : Namespace.DESTINATION;

  const trackMenuOpen = () => {
    analytics.track(namespaceType, Action.SELECTION_OPENED, {
      actionDescription: "Opened connector type selection",
    });
  };

  const trackNoOptionMessage = (inputValue: string) => {
    analytics.track(namespaceType, Action.NO_MATCHING_CONNECTOR, {
      actionDescription: "Connector query without results",
      query: inputValue,
    });
  };

  const trackConnectorSelection = (connectorId: string, connectorName: string) => {
    analytics.track(namespaceType, Action.SELECT, {
      actionDescription: `${capitalize(formType)} connector type selected`,
      [`connector_${formType}`]: connectorName,
      [`connector_${formType}_definition_id`]: connectorId,
    });
  };

  return { trackMenuOpen, trackNoOptionMessage, trackConnectorSelection };
};
