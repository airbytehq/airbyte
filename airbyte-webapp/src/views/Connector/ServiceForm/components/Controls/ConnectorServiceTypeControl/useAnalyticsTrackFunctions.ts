import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

export const useAnalyticsTrackFunctions = (formType: "source" | "destination") => {
  const analytics = useAnalyticsService();

  const getNamespace = (formType: "source" | "destination") =>
    formType === "source" ? Namespace.SOURCE : Namespace.DESTINATION;

  const trackMenuOpen = () => {
    analytics.track(getNamespace(formType), Action.SELECTION_OPENED, {
      actionDescription: "Opened connector type selection",
    });
  };

  const trackNoOptionMessage = (inputValue: string) => {
    analytics.track(getNamespace(formType), Action.NO_MATCHING_CONNECTOR, {
      actionDescription: "Connector query without results",
      query: inputValue,
    });
  };

  return { trackMenuOpen, trackNoOptionMessage };
};
