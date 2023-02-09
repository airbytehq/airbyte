import React, { Fragment } from "react";
import { components, OptionProps } from "react-select";
import styled from "styled-components";

import { CheckBox } from "components/ui/CheckBox";

import { DropDownText } from "./DropDownText";
import { OptionType } from "../DropDown";

export type DropDownOptionProps = {
  data: { disabled: boolean; index: number; fullText?: boolean } & DropDownOptionDataItem;
} & OptionProps<OptionType, boolean>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface DropDownOptionDataItem<Value = any, Config = any> {
  label?: string;
  value?: Value;
  groupValue?: string;
  groupValueText?: string;
  img?: React.ReactNode;
  primary?: boolean;
  secondary?: boolean;
  config?: Config;
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
        onClick={(event) => {
          // This custom onClick handler prevents the click event from bubbling up outside of the option
          // for cases where the Dropdown is a child of a clickable parent such as a table row.
          props.selectOption(props.data);
          event.stopPropagation();
          // The checkbox does not work properly without this
          event.preventDefault();
        }}
      >
        <DropDownText primary={props.data.primary} secondary={props.data.secondary} fullText={props.data.fullText}>
          {props.isMulti && (
            <>
              <CheckBox checked={props.isSelected} onChange={() => props.selectOption(props.data)} />{" "}
            </>
          )}
          {Array.isArray(props.label)
            ? props.label
                .map<React.ReactNode>((node, index) => <Fragment key={index}>{node}</Fragment>)
                .reduce((prev, curr) => [prev, " | ", curr])
            : props.label}
        </DropDownText>
        {props.data.img || null}
      </OptionView>
    </components.Option>
  );
};
