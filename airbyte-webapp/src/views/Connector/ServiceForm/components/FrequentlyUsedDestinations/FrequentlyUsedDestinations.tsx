import { useField } from "formik";
import React from "react";
import { useIntl } from "react-intl";

import { ConnectorCard } from "components";
import { SlickSlider } from "components/ui/SlickSlider";
import { Spinner } from "components/ui/Spinner";

import { DestinationConnectorCard } from "../../types";
import styles from "./FrequentlyUsedDestinations.module.scss";

export interface FrequentlyUsedDestinationsProps {
  propertyPath: string;
  destinations: DestinationConnectorCard[];
  onDestinationSelect?: (
    id: string,
    trackParams?: { actionDescription: string; connector_destination_suggested: boolean }
  ) => void;
  isLoading?: boolean;
}

export const FrequentlyUsedDestinations: React.FC<FrequentlyUsedDestinationsProps> = ({
  propertyPath,
  destinations,
  onDestinationSelect,
  isLoading,
}) => {
  const [, , { setValue }] = useField(propertyPath);
  const { formatMessage } = useIntl();

  if (!destinations?.length) {
    return null;
  }
  const onSlideClick = (id: string) => {
    setValue(id);
    onDestinationSelect?.(id, {
      actionDescription: "Suggested destination connector type selected",
      connector_destination_suggested: true,
    });
  };
  return (
    <div className={styles.container}>
      {isLoading ? (
        <div className={styles.spinnerContainer}>
          <Spinner small />
        </div>
      ) : (
        <SlickSlider title={formatMessage({ id: "destinations.frequentlyUsed" })}>
          {destinations.map(({ destinationDefinitionId, name, icon, releaseStage }, index) => (
            <button key={index} className={styles.card} onClick={() => onSlideClick(destinationDefinitionId)}>
              <ConnectorCard connectionName={name} icon={icon} releaseStage={releaseStage} fullWidth />
            </button>
          ))}
        </SlickSlider>
      )}
    </div>
  );
};
