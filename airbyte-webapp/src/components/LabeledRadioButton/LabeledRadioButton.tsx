import React from "react";
import styled from "styled-components";

import { RadioButton } from "components/ui/RadioButton";

type IProps = {
  message?: React.ReactNode;
  label?: React.ReactNode;
  className?: string;
} & React.InputHTMLAttributes<HTMLInputElement>;

const ControlContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 6px;
`;

const Label = styled.label<{ disabled?: boolean }>`
  padding-left: 7px;
  font-size: 15px;
  line-height: 18px;
  font-weight: 500;
  color: ${({ theme, disabled }) => (disabled ? theme.greyColor40 : theme.darkPrimaryColor)};
  cursor: ${({ disabled }) => (disabled ? "auto" : "pointer")};
`;

const AdditionMessage = styled.span`
  padding-left: 5px;
  color: ${({ theme }) => theme.greyColor40};
  font-size: 13px;

  & a {
    text-decoration: underline;
    color: ${({ theme }) => theme.primaryColor};
  }
`;

const LabeledRadioButton: React.FC<IProps> = (props) => (
  <ControlContainer className={props.className}>
    <RadioButton {...props} id={`radiobutton-${props.id || props.name}`} disabled={props.disabled} />
    <Label disabled={props.disabled} htmlFor={`radiobutton-${props.id || props.name}`}>
      {props.label}
      <AdditionMessage>{props.message}</AdditionMessage>
    </Label>
  </ControlContainer>
);

export default LabeledRadioButton;
