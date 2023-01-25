import { faArrowDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { SourceDefinitionRead } from "core/request/AirbyteClient";
import { useDocumentationPanelContext } from "views/Connector/ConnectorDocumentationLayout/DocumentationPanelContext";

import octaviaWorker from "./octavia-worker.png";
import styles from "./ResourceNotAvailable.module.scss";
import { useAnalyticsTrackFunctions } from "../useAnalyticsTrackFunctions";

export const ResourceNotAvailable: React.FC<
  React.PropsWithChildren<{
    activeTab: "erd" | "schema";
    isRequested: boolean;
    setRequested: (val: boolean) => void;
  }>
> = ({ activeTab, setRequested, isRequested }) => {
  const { selectedConnectorDefinition } = useDocumentationPanelContext();
  const { trackRequest } = useAnalyticsTrackFunctions();

  return (
    <div className={styles.requestContainer}>
      <img src={octaviaWorker} alt="" />
      {isRequested ? (
        <Text size="lg">
          <FormattedMessage id="sources.request.thankYou" />
        </Text>
      ) : (
        <>
          <Text size="lg">
            <FormattedMessage id="sources.request.prioritize" />
          </Text>
          <FontAwesomeIcon icon={faArrowDown} />
          <Button
            variant="primary"
            onClick={() => {
              trackRequest({
                sourceDefinitionId: (selectedConnectorDefinition as SourceDefinitionRead).sourceDefinitionId,
                connectorName: selectedConnectorDefinition.name,
                requestType: activeTab,
              });
              setRequested(true);
            }}
          >
            <FormattedMessage id={`sources.request.button.${activeTab}`} />
          </Button>
        </>
      )}
    </div>
  );
};
