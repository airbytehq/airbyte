import React from "react";
import styled from "styled-components";
import { components, OptionProps, OptionTypeBase } from "react-select";

import CheckBox from "components/base/CheckBox";
import Text from "./Text";

export type IProps = {
  data: { disabled: boolean; index: number; fullText?: boolean } & IDataItem;
} & OptionProps<OptionTypeBase, false>;

export type IDataItem = {
  label?: string;
  value?: any;
  groupValue?: string;
  groupValueText?: string;
  img?: React.ReactNode;
  primary?: boolean;
  secondary?: boolean;
  config?: any;
};

export const OptionView = styled.div<{
  isSelected?: boolean;
  isDisabled?: boolean;
}>`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  color: ${({ isSelected, theme }) =>
    isSelected ? theme.primaryColor : theme.textColor};
  background: ${({ isSelected, theme }) =>
    isSelected ? theme.primaryColor12 : theme.whiteColor};
  border: none;
  padding: 10px 16px;
  font-size: 14px;
  line-height: 19px;

  &:hover {
    background: ${({ isSelected, theme }) =>
      isSelected ? theme.primaryColor12 : theme.greyColor0};
  }
`;

const Option: React.FC<IProps> = (props) => {
  return (
    <components.Option {...props}>
      <OptionView
        data-testid={props.data.label}
        isSelected={props.isSelected && !props.isMulti}
        isDisabled={props.isDisabled}
      >
        <Text
          primary={props.data.primary}
          secondary={props.data.secondary}
          fullText={props.data.fullText}
        >
          {props.isMulti && (
            <>
              <CheckBox
                checked={props.isSelected}
                onChange={() => props.selectOption(props.data)}
              />{" "}
            </>
          )}
          {props.label}
        </Text>
        {props.data.img || null}
      </OptionView>
    </components.Option>
  );
};

export default Option;
