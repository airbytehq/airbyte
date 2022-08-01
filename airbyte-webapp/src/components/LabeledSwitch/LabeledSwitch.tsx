import classNames from "classnames";
import React from "react";

import { CheckBox, Switch } from "components/base";

import styles from "./LabeledSwitch.module.scss";

interface LabeledSwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  message?: React.ReactNode;
  label?: React.ReactNode;
  checkbox?: boolean;
  loading?: boolean;
}

export const LabeledSwitch: React.FC<LabeledSwitchProps> = (props) => (
  <div className={styles.labeledSwitch}>
    <span>
      {props.checkbox ? (
        <CheckBox {...props} id={`toggle-${props.name}`} />
      ) : (
        <Switch {...props} id={`toggle-${props.name}`} />
      )}
    </span>

    <label
      className={classNames(styles.label, {
        [styles.disabled]: props.disabled,
      })}
      htmlFor={`toggle-${props.name}`}
    >
      {props.label}
      <span className={styles.additionalMessage}>{props.message}</span>
    </label>
  </div>
);
