import { useAnalyticsService } from "hooks/services/Analytics/useAnalyticsService";

type Values = {
  connectorType: string;
  name: string;
  website: string;
  email?: string;
};

const useRequestConnector = (): {
  requestConnector: (conn: Values) => void;
} => {
  const analyticsService = useAnalyticsService();

  const requestConnector = (values: Values) => {
    analyticsService.track("Request a Connector", {
      email: values.email,
      connector_site: values.website,
      connector_source: values.connectorType === "source" ? values.name : "",
      connector_destination:
        values.connectorType === "destination" ? values.name : "",
    });
  };

  return {
    requestConnector,
  };
};
export default useRequestConnector;
