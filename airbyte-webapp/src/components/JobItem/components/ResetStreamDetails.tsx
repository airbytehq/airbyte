import classNames from "classnames";
import React from "react";

import styles from "./ResetStreamDetails.module.scss";

interface IProps {
  names: string[];
  isOpen?: boolean;
}

export const ResetStreamsDetails: React.FC<IProps> = ({ names, isOpen }) => (
  <p className={classNames(styles.textContainer, { [styles.open]: isOpen })}>
    {names.map((name) => (
      <span key={name} className={styles.text}>
        {name}
      </span>
    ))}
  </p>
);
