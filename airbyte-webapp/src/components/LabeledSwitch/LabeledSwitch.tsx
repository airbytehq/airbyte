import React from "react";
import styled from "styled-components";

import { CheckBox } from "components/base";
import { HeadlessSwitch } from "components/base/Switch/HeadlessSwitch";

interface LabeledSwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange"> {
  message?: React.ReactNode;
  label?: React.ReactNode;
  checkbox?: boolean;
  loading?: boolean;
  onChange: (checked: boolean) => void;
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
      <CheckBox {...props} id={`toggle-${props.name}`} onChange={(event) => props.onChange(event?.target.checked)} />
    ) : (
      <HeadlessSwitch {...props} id={`toggle-${props.name}`} onChange={(checked) => props.onChange(checked)} />
    )}

    <Label disabled={props.disabled} htmlFor={`toggle-${props.name}`}>
      {props.label}
      <AdditionMessage>{props.message}</AdditionMessage>
    </Label>
  </ToggleContainer>
);
