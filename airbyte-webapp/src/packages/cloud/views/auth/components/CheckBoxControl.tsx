import React from "react";
import styled from "styled-components";

import { CheckBox } from "components/ui/CheckBox";

type IProps = {
  message?: React.ReactNode;
  label?: React.ReactNode;
  checkbox?: boolean;
} & React.InputHTMLAttributes<HTMLInputElement>;

const ToggleContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Label = styled.label<{ disabled?: boolean }>`
  padding-left: 7px;
  font-size: 11px;
  line-height: 13px;
  color: ${({ theme }) => theme.textColor};
  cursor: pointer;
`;

const BigCheckBox = styled(CheckBox)`
  height: 25px;
  width: 25px;
  min-width: 25px;
  background: ${({ theme, checked }) => (checked ? theme.primaryColor : theme.whiteColor)};
  border: ${({ theme, checked }) => (checked ? theme.primaryColor : theme.textColor)} 2px solid;
  color: ${({ theme }) => theme.whiteColor};
  font-size: 18px;
  line-height: 18px;
`;

const CheckBoxControl: React.FC<IProps> = (props) => (
  <ToggleContainer>
    <BigCheckBox {...props} id={`checkbox-${props.name}`} />
    <Label disabled={props.disabled} htmlFor={`checkbox-${props.name}`}>
      {props.label}
    </Label>
  </ToggleContainer>
);

export default CheckBoxControl;
