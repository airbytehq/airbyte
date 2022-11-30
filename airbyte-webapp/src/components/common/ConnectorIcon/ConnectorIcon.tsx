import classNames from "classnames";
import React from "react";

import { getIcon } from "utils/imageUtils";

import styles from "./ConnectorIcon.module.scss";

interface ConnectorIconProps {
  icon?: string;
  className?: string;
}

export const ConnectorIcon: React.FC<ConnectorIconProps> = ({ className, icon }) => (
  <div className={classNames(styles.content, className)} aria-hidden="true">
    {getIcon(icon)}
  </div>
);
