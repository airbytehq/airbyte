import { useField } from "formik";
import React from "react";
import { useIntl } from "react-intl";

import { ContentCard, ConnectorCard } from "components";

import { DestinationDefinitionReadWithLatestTag } from "services/connector/DestinationDefinitionService";

import styles from "./StartWithDestination.module.scss";

interface StartWithDestinationProps {
  destination: DestinationDefinitionReadWithLatestTag | undefined;
  onDestinationSelect: ((id: string) => void) | undefined;
}

export const StartWithDestination: React.FC<StartWithDestinationProps> = ({ destination, onDestinationSelect }) => {
  // since we will use the component just in one place we can hardcode the useField()
  const [, , { setValue }] = useField("serviceType");
  const { formatMessage } = useIntl();

  if (!destination) {
    return null;
  }
  const { icon, releaseStage, name, destinationDefinitionId } = destination;

  const connectorCardClickHandler = () => {
    setValue(destinationDefinitionId);
    if (onDestinationSelect) {
      onDestinationSelect(destinationDefinitionId);
    }
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.container} onClick={connectorCardClickHandler}>
        <ContentCard>
          <div className={styles.connectorCardWrapper}>
            <ConnectorCard
              icon={icon}
              releaseStage={releaseStage}
              connectionName={formatMessage({ id: "destinations.dontHaveYourOwnDestination" })}
              connectorName={formatMessage({ id: "destinations.startWith" }, { name })}
              fullWidth
            />
          </div>
        </ContentCard>
      </div>
    </div>
  );
};
