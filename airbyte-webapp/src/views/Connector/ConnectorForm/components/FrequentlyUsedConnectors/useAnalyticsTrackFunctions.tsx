import { useCallback } from "react";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

export const useAnalyticsTrackFunctions = () => {
  const analytics = useAnalyticsService();

  const trackSelectedSuggestedDestination = useCallback(
    (destinationDefinitionId: string, connectorName: string) => {
      analytics.track(Namespace.DESTINATION, Action.SELECT, {
        actionDescription: "Suggested destination connector type selected",
        connector_destination: connectorName,
        connector_destination_definition_id: destinationDefinitionId,
        connector_destination_suggested: true,
      });
    },
    [analytics]
  );
  return { trackSelectedSuggestedDestination };
};
