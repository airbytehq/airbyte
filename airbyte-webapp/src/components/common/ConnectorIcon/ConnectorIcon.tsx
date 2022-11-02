import React from "react";

import { getIcon } from "utils/imageUtils";

import styles from "./ConnectorIcon.module.scss";

interface Props {
  icon?: string;
  className?: string;
  small?: boolean;
}

export const ConnectorIcon: React.FC<Props> = ({ icon }) => (
  <div className={styles.content} aria-hidden="true">
    {getIcon(icon)}
  </div>
);
