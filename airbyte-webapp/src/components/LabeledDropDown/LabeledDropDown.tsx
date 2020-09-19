import React from "react";
import styled from "styled-components";

import Label from "../Label/Label";
import DropDown from "../DropDown";
import { IProps as DropDownProps } from "../DropDown/DropDown";

type IProps = {
  className?: string;
  error?: boolean;
  success?: boolean;
  message?: React.ReactNode;
  labelAdditionLength?: number;
  label?: React.ReactNode;
} & DropDownProps;

const InputContainer = styled.div`
  width: 100%;
  display: inline-block;
`;

const LabeledDropDown: React.FC<IProps> = props => (
  <InputContainer className={props.className}>
    <Label
      error={props.error}
      success={props.success}
      message={props.message}
      additionLength={props.labelAdditionLength}
    >
      {props.label}
    </Label>
    <DropDown {...props} />
  </InputContainer>
);

export default LabeledDropDown;
