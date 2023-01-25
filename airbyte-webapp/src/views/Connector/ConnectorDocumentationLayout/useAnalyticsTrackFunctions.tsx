import { useCallback } from "react";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

export const useAnalyticsTrackFunctions = () => {
  const analytics = useAnalyticsService();

  const trackRequest = useCallback(
    ({
      sourceDefinitionId,
      connectorName,
      requestType,
    }: {
      sourceDefinitionId: string;
      connectorName: string;
      requestType: "schema" | "erd";
    }) => {
      analytics.track(Namespace.SCHEMA, Action.REQUEST, {
        actionDescription: `Requested source ${requestType}`,
        connector_source: connectorName,
        connector_source_definition_id: sourceDefinitionId,
        request_type: requestType,
      });
    },
    [analytics]
  );
  return { trackRequest };
};
