import { useIntl } from "react-intl";

import { Action, Namespace } from "core/analytics";
import { useAnalyticsService } from "hooks/services/Analytics";

import { AuthenticationSection } from "./AuthenticationSection";
import { BuilderCard } from "./BuilderCard";
import { BuilderConfigView } from "./BuilderConfigView";
import { BuilderField } from "./BuilderField";
import { BuilderTitle } from "./BuilderTitle";
import styles from "./GlobalConfigView.module.scss";

export const GlobalConfigView: React.FC = () => {
  const { formatMessage } = useIntl();
  const analyticsService = useAnalyticsService();

  return (
    <BuilderConfigView heading={formatMessage({ id: "connectorBuilder.globalConfiguration" })}>
      {/* Not using intl for the labels and tooltips in this component in order to keep maintainence simple */}
      <BuilderTitle path="global.connectorName" label="Connector Name" size="lg" />
      <BuilderCard className={styles.content}>
        <BuilderField
          type="string"
          path="global.urlBase"
          label="API URL"
          tooltip="Base URL of the source API"
          onBlur={(value: string) => {
            if (value) {
              analyticsService.track(Namespace.CONNECTOR_BUILDER, Action.API_URL_CREATE, {
                actionDescription: "Base API URL filled in",
                api_url: value,
              });
            }
          }}
        />
      </BuilderCard>
      <AuthenticationSection />
    </BuilderConfigView>
  );
};
