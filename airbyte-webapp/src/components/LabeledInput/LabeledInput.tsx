import React from "react";

import { Input, InputProps } from "components/base";
import { ControlLabels } from "components/LabeledControl";

type IProps = {
  success?: boolean;
  message?: React.ReactNode;
  label?: React.ReactNode;
  labelAdditionLength?: number;
} & InputProps;

const LabeledInput: React.FC<IProps> = (props) => (
  <ControlLabels
    error={props.error}
    success={props.success}
    message={props.message}
    label={props.label}
    labelAdditionLength={props.labelAdditionLength}
  >
    <Input {...props} />
  </ControlLabels>
);

export default LabeledInput;
