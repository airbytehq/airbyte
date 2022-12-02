import { faExclamationCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";

import { Tooltip } from "components/ui/Tooltip";

import { SchemaChange } from "core/request/AirbyteClient";

import styles from "./ChangesStatusIcon.module.scss";

interface ChangesStatusIconProps {
  schemaChange?: SchemaChange;
}

export const ChangesStatusIcon: React.FC<ChangesStatusIconProps> = ({ schemaChange = "no_change" }) => {
  if (schemaChange === "no_change") {
    return null;
  }
  const iconStyle = classnames(styles.changesIcon, {
    [styles.breaking]: schemaChange === "breaking",
    [styles.nonBreaking]: schemaChange === "non_breaking",
  });
  const tooltipComponent = <FormattedMessage id={`tables.connections.changes.${schemaChange}`} />;
  return (
    <Tooltip
      containerClassName={styles.tooltipContainer}
      control={<FontAwesomeIcon className={iconStyle} icon={faExclamationCircle} size="2x" />}
    >
      {tooltipComponent}
    </Tooltip>
  );
};
