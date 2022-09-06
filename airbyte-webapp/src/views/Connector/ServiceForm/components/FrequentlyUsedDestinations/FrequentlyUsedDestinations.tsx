import { useField } from "formik";
import { useIntl } from "react-intl";

import ConnectorCard from "components/ConnectorCard";
import { ConnectorCardProps } from "components/ConnectorCard/ConnectorCard";
import { SlickSlider } from "components/SlickSlider";
import Spinner from "components/Spinner";

import { DestinationDefinitionId } from "core/request/AirbyteClient";

import styles from "./FrequentlyUsedDestinations.module.scss";

export interface FrequentlyUsedDestination extends ConnectorCardProps {
  destinationDefinitionId: DestinationDefinitionId;
}

export interface FrequentlyUsedDestinationsProps {
  propertyPath: string;
  destinations: FrequentlyUsedDestination[];
  onDestinationSelect: ((id: string) => void) | undefined;
  isLoading?: boolean;
}

export const FrequentlyUsedDestinations = ({
  propertyPath,
  destinations,
  onDestinationSelect,
  isLoading,
}: FrequentlyUsedDestinationsProps) => {
  const [, , { setValue }] = useField(propertyPath);
  const { formatMessage } = useIntl();

  if (!destinations?.length) {
    return null;
  }
  const onSlideClick = (id: string) => {
    setValue(id);
    if (onDestinationSelect) {
      onDestinationSelect(id);
    }
  };
  return (
    <div className={styles.container}>
      {isLoading ? (
        <div className={styles.spinnerContainer}>
          <Spinner small />
        </div>
      ) : (
        <SlickSlider title={formatMessage({ id: "destinations.frequentlyUsed" })}>
          {destinations.map(({ destinationDefinitionId, connectionName, connectorName, icon, releaseStage }, index) => (
            <div key={index} onClick={() => onSlideClick(destinationDefinitionId)}>
              <div className={styles.card}>
                <ConnectorCard
                  connectionName={connectionName}
                  connectorName={connectorName}
                  icon={icon}
                  releaseStage={releaseStage}
                />
              </div>
            </div>
          ))}
        </SlickSlider>
      )}
    </div>
  );
};
