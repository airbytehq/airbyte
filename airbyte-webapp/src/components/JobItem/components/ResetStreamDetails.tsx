import classNames from "classnames";
import React from "react";

import styles from "./ResetStreamDetails.module.scss";

interface ResetStreamsDetailsProps {
  names: string[];
  isOpen?: boolean;
}

export const ResetStreamsDetails: React.FC<ResetStreamsDetailsProps> = ({ isOpen }) => (
  <p className={classNames(styles.textContainer, { [styles.open]: isOpen })}>
    {[
      "eqwefgqwegqweg",
      "eqwegqwegqweg",
      "eqwefgqwegqweg",
      "eqwegqwegqweg",
      "eqwefgqwegqweg",
      "eqwegqwegqweg",
      "eqwefgqwegqweg",
      "eqwegqwegqweg",
      "eqwefgqwegqweg",
      "eqwegqwegqweg",
      "eqwefgqwegqweg",
      "eqwegqwegqweg",
      "eqwefgqwegqweg",
      "eqwegqwegqweg",
      "eqwefgqwegqweg",
      "eqwegqwegqweg",
    ].map((name) => (
      <span key={name} className={styles.text}>
        {name}
      </span>
    ))}
  </p>
);
