import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { Heading } from "components/ui/Heading";

import { useConnectionEditService } from "hooks/services/ConnectionEdit/ConnectionEditService";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { getIcon } from "utils/imageUtils";

import styles from "./StreamConnectionHeader.module.scss";

const renderIcon = (icon?: string): JSX.Element => <div className={styles.icon}>{getIcon(icon)}</div>;

export const StreamConnectionHeader: React.FC = () => {
  const {
    connection: { source, destination },
  } = useConnectionEditService();
  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  return (
    <div className={styles.container}>
      <div className={styles.connector}>
        {renderIcon(sourceDefinition.icon)}{" "}
        <Heading as="h5" size="sm">
          <FormattedMessage id="connectionForm.sourceTitle" />
        </Heading>
      </div>
      <FontAwesomeIcon icon={faArrowRight} />
      <div className={styles.connector}>
        {renderIcon(destinationDefinition.icon)}{" "}
        <Heading as="h5" size="sm">
          <FormattedMessage id="connectionForm.destinationTitle" />
        </Heading>
      </div>
    </div>
  );
};
