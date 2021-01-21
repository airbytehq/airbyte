import React from "react";
import styled from "styled-components";

import Input from "../Input";
import Label from "../Label/Label";
import { InputProps } from "../Input/types";

type IProps = {
  success?: boolean;
  message?: React.ReactNode;
  labelAdditionLength?: number;
  label?: React.ReactNode;
} & InputProps;

const InputContainer = styled.div`
  width: 100%;
  display: inline-block;
`;

const LabeledInput: React.FC<IProps> = props => (
  <InputContainer>
    <Label
      error={props.error}
      success={props.success}
      message={props.message}
      additionLength={props.labelAdditionLength}
    >
      {props.label}
    </Label>
    <Input {...props} />
  </InputContainer>
);

export default LabeledInput;
