import { faUser } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { ControlLabels } from "components/LabeledControl";
import { Tooltip } from "components/ui/Tooltip";

import styles from "./UserInputField.module.scss";

export const UserInputField: React.FC<{ label: string; tooltip: string }> = ({ label, tooltip }) => {
  return (
    <ControlLabels className={styles.container} label={label} infoTooltipContent={tooltip}>
      <Tooltip control={<FontAwesomeIcon icon={faUser} className={styles.icon} />}>
        <FormattedMessage id="connectorBuilder.setInUserInput" />
      </Tooltip>
    </ControlLabels>
  );
};
