import React from "react";

import { ControlLabels, ControlLabelsProps } from "components/LabeledControl";
import { Input, InputProps } from "components/ui/Input";

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
