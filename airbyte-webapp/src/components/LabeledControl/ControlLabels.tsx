import className from "classnames";
import React from "react";

import { Text } from "components/base/Text";
import { InfoTooltip } from "components/base/Tooltip";
import Label from "components/Label";

import styles from "./ControlLabels.module.scss";

export interface ControlLabelsProps {
  className?: string;
  error?: boolean;
  success?: boolean;
  nextLine?: boolean;
  message?: React.ReactNode;
  errorMessage?: React.ReactNode;
  labelAdditionLength?: number;
  label?: React.ReactNode;
  infoMessage?: React.ReactNode;
  optional?: boolean;
}

const ControlLabels: React.FC<ControlLabelsProps> = (props) => (
  <div className={className(styles.controlContainer, props.className)}>
    <Label
      className={styles.label}
      error={props.error}
      success={props.success}
      message={props.message}
      additionLength={props.labelAdditionLength}
      nextLine={props.nextLine}
    >
      {props.label}
      {props.infoMessage && (
        <InfoTooltip className={styles.tooltip} placement="top-start">
          {props.infoMessage}
        </InfoTooltip>
      )}
      {props.optional && (
        <Text size="sm" className={styles.optionalText}>
          Optional
        </Text>
      )}
      {props.errorMessage && <Text className={styles.errorMessage}>{props.errorMessage}</Text>}
    </Label>
    {props.children}
  </div>
);

export { ControlLabels };
