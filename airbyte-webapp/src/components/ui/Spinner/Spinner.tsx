import classnames from "classnames";
import React from "react";

import styles from "./Spinner.module.scss";

interface SpinnerProps {
  small?: boolean;
}

export const Spinner: React.FC<SpinnerProps> = ({ small }) => (
  <div className={classnames(styles.spinner, { [styles.small]: small })} />
);
