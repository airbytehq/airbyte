import classNames from "classnames";
import React from "react";

import { CheckBox } from "components/ui/CheckBox";
import { Switch } from "components/ui/Switch";

import styles from "./LabeledSwitch.module.scss";

interface LabeledSwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size"> {
  message?: React.ReactNode;
  label?: React.ReactNode;
  checkbox?: boolean;
  loading?: boolean;
  id?: string;
}

export const LabeledSwitch: React.FC<LabeledSwitchProps> = (props) => {
  const switchId = props.id ?? `toggle-${props.name}`;

  return (
    <div className={classNames(styles.labeledSwitch, props.className)}>
      <span>{props.checkbox ? <CheckBox {...props} id={switchId} /> : <Switch {...props} id={switchId} />}</span>

      <label
        className={classNames(styles.label, {
          [styles.disabled]: props.disabled,
        })}
        htmlFor={switchId}
      >
        {props.label}
        <span className={styles.additionalMessage}>{props.message}</span>
      </label>
    </div>
  );
};
