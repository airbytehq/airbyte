import React from "react";
import classNames from "classnames";
import styles from "./Chip.module.css";

export const Chip = ({ className, ...rest }) => (
  <span className={classNames(className, styles.chip)} {...rest} />
);
