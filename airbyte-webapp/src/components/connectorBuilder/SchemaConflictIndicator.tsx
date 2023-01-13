import { faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { Tooltip } from "components/ui/Tooltip";

import styles from "./SchemaConflictIndicator.module.scss";

export const SchemaConflictIndicator: React.FC = () => (
  <Tooltip control={<FontAwesomeIcon icon={faWarning} className={styles.schemaConflictIcon} />}>
    <FormattedMessage id="connectorBuilder.differentSchemaDescription" />
  </Tooltip>
);
