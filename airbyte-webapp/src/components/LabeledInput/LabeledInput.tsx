import React from "react";

import { ControlLabels, ControlLabelsProps } from "components/LabeledControl";
import { Input, InputProps } from "components/ui/Input";

type LabeledInputProps = Pick<ControlLabelsProps, "success" | "message" | "label" | "labelAdditionLength"> &
  InputProps & { className?: string };

const LabeledInput: React.FC<LabeledInputProps> = ({
  error,
  success,
  message,
  label,
  labelAdditionLength,
  className,
  ...inputProps
}) => (
  <ControlLabels
    error={error}
    success={success}
    message={message}
    label={label}
    className={className}
    labelAdditionLength={labelAdditionLength}
  >
    <Input {...inputProps} error={error} />
  </ControlLabels>
);

export default LabeledInput;
