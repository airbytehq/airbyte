import React from "react";
import styled from "styled-components";

import { CheckBox, Switch } from "components/base";

interface LabeledSwitchProps extends React.InputHTMLAttributes<HTMLInputElement> {
  message?: React.ReactNode;
  label?: React.ReactNode;
  checkbox?: boolean;
  loading?: boolean;
}

const ToggleContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Label = styled.label<{ disabled?: boolean }>`
  padding-left: 7px;
  font-size: 13px;
  line-height: 16px;
  color: ${({ theme, disabled }) => (disabled ? theme.greyColor40 : theme.textColor)};
  cursor: ${({ disabled }) => (disabled ? "auto" : "pointer")};
`;

const AdditionMessage = styled.span`
  padding-left: 5px;
  color: ${({ theme }) => theme.greyColor40};

  & a {
    text-decoration: underline;
    color: ${({ theme }) => theme.primaryColor};
  }
`;

export const LabeledSwitch: React.FC<LabeledSwitchProps> = (props) => (
  <ToggleContainer>
    {props.checkbox ? (
      <CheckBox {...props} id={`toggle-${props.name}`} />
    ) : (
      <Switch {...props} id={`toggle-${props.name}`} />
    )}

    <Label disabled={props.disabled} htmlFor={`toggle-${props.name}`}>
      {props.label}
      <AdditionMessage>{props.message}</AdditionMessage>
    </Label>
  </ToggleContainer>
);
