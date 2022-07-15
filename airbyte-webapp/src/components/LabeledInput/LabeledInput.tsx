import React from "react";

import { Input, InputProps } from "components/base";
import { ControlLabels, ControlLabelsProps } from "components/LabeledControl";

type LabeledInputProps = Pick<ControlLabelsProps, "success" | "message" | "label" | "labelAdditionLength"> & InputProps;

const LabeledInput: React.FC<LabeledInputProps> = ({
  error,
  success,
  message,
  label,
  labelAdditionLength,
  ...inputProps
}) => (
  <ControlLabels
    error={error}
    success={success}
    message={message}
    label={label}
    labelAdditionLength={labelAdditionLength}
  >
    <Input {...inputProps} error={error} />
  </ControlLabels>
);

export default LabeledInput;
