import classnames from "classnames";
import React from "react";

import styles from "./Spinner.module.scss";

interface SpinnerProps {
  small?: boolean;
  className?: string;
}

const Spinner: React.FC<SpinnerProps> = ({ small, className }) => (
  <div className={classnames(styles.spinner, className, { [styles.small]: small })} />
);

export default Spinner;
