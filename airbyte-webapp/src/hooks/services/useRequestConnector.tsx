import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";

interface Values {
  connectorType: string;
  name: string;
  additionalInfo?: string;
  email?: string;
}

const useRequestConnector = (): {
  requestConnector: (conn: Values) => void;
} => {
  const analyticsService = useAnalyticsService();

  const requestConnector = (values: Values) => {
    analyticsService.track(Namespace.CONNECTOR, Action.REQUEST, {
      actionDescription: "Request new connector",
      email: values.email,
      // This parameter has a legacy name from when it was only the webpage, but we wanted to keep the parameter
      // name the same after renaming the field to additional information
      connector_site: values.additionalInfo,
      connector_source: values.connectorType === "source" ? values.name : "",
      connector_destination: values.connectorType === "destination" ? values.name : "",
    });
  };

  return {
    requestConnector,
  };
};
export default useRequestConnector;
