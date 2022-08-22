import classnames from "classnames";
import React from "react";

import styles from "./Spinner.module.scss";

interface SpinnerProps {
  small?: boolean;
}

const Spinner: React.FC<SpinnerProps> = ({ small }) => (
  <div className={classnames(styles.spinner, { [styles.small]: small })} />
);

export default Spinner;
