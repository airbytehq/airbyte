import React from "react";
import classNames from "classnames";
import styles from "./Callout.module.css";

export const Callout = ({ className, ...rest }) => (
  <div className={classNames(className, styles.callout)} {...rest} />
);
