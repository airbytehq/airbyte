import React from "react";
import { components, OptionProps } from "react-select";
import styled from "styled-components";

import { CheckBox } from "components/ui/CheckBox";

import { OptionType } from "../DropDown";
import { DropDownText } from "./DropDownText";

export type DropDownOptionProps = {
  data: { disabled: boolean; index: number; fullText?: boolean } & DropDownOptionDataItem;
} & OptionProps<OptionType, boolean>;

export interface DropDownOptionDataItem {
  label?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  value?: any;
  groupValue?: string;
  groupValueText?: string;
  img?: React.ReactNode;
  primary?: boolean;
  secondary?: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  config?: any;
}

export const OptionView = styled.div<{
  isFocused?: boolean;
  isSelected?: boolean;
  isDisabled?: boolean;
}>`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  color: ${({ isSelected, theme }) => (isSelected ? theme.primaryColor : theme.textColor)};
  background: ${({ isSelected, isFocused, theme }) =>
    isSelected ? theme.primaryColor12 : isFocused ? theme.grey100 : theme.whiteColor};
  border: none;
  padding: 10px 16px;
  font-size: 14px;
  line-height: 19px;

  &:hover {
    background: ${({ isSelected, theme }) => (isSelected ? theme.primaryColor12 : theme.grey100)};
  }
`;

export const DropDownOption: React.FC<DropDownOptionProps> = (props) => {
  const dataTestId = props.data.testId
    ? props.data.testId
    : !["object", "array"].includes(typeof props.data.label)
    ? props.data.label
    : `select_value_${props.data.value}`;

  return (
    <components.Option {...props}>
      <OptionView
        data-testid={dataTestId}
        isSelected={props.isSelected && !props.isMulti}
        isDisabled={props.isDisabled}
        isFocused={props.isFocused}
      >
        <DropDownText primary={props.data.primary} secondary={props.data.secondary} fullText={props.data.fullText}>
          {props.isMulti && (
            <>
              <CheckBox checked={props.isSelected} onChange={() => props.selectOption(props.data)} />{" "}
            </>
          )}
          {props.label}
        </DropDownText>
        {props.data.img || null}
      </OptionView>
    </components.Option>
  );
};
