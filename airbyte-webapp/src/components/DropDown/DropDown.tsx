import React from "react";
import { DropdownList } from "react-widgets";
import styled from "styled-components";

import "react-widgets/dist/css/react-widgets.css";
import { useIntl } from "react-intl";
import ListItem, { IDataItem } from "./components/ListItem";
import ValueInput from "./components/ValueInput";
import WithButtonItem from "./components/WithButtonItem";

export type IProps = {
  disabled?: boolean;
  hasFilter?: boolean;
  placeholder?: string;
  filterPlaceholder?: string;
  value?: string;
  data: Array<IDataItem>;
  onSelect?: (item: IDataItem) => void;
  withButton?: boolean;
  withBorder?: boolean;
  textButton?: string;
};

const StyledDropdownList = styled(DropdownList)<{
  disabled?: boolean;
  withBorder?: boolean;
}>`
  text-align: left;
  &.rw-state-disabled {
    pointer-events: none;
    cursor: auto;

    & .rw-btn {
      opacity: 0;
    }
    & .rw-placeholder,
    & .rw-input {
      color: ${({ theme }) => theme.greyColor40};
    }
  }

  & > .rw-widget-container {
    height: ${({ withBorder }) => (withBorder ? 31 : 36)}px;
    box-shadow: none;
    border: 1px solid
      ${({ theme, withBorder }) =>
        withBorder ? theme.greyColor30 : theme.greyColor0};
    background: ${({ theme }) => theme.greyColor0};
    border-radius: 4px;

    &:hover {
      border-color: ${({ theme }) => theme.greyColor20};
      background: ${({ theme }) => theme.greyColor20};
    }
  }

  & .rw-btn {
    color: ${({ theme }) => theme.greyColor40};
  }

  & .rw-filter-input {
    margin: 0;
    border: none;
    border-radius: 0;
    border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
    padding: 10px 16px;
  }

  & .rw-placeholder {
    color: ${({ theme }) => theme.textColor};
  }

  & .rw-popup {
    border: 0.5px solid ${({ theme }) => theme.greyColor20};
    border-radius: 4px;
    box-shadow: 0 8px 10px 0 rgba(11, 10, 26, 0.04),
      0 3px 14px 0 rgba(11, 10, 26, 0.08), 0 5px 5px 0 rgba(11, 10, 26, 0.12);
  }

  & .rw-list-option.rw-state-focus,
  & .rw-list-option,
  & .rw-list-empty {
    color: ${({ theme }) => theme.textColor};
    border: none;
    padding: 10px 16px;
    font-size: 14px;
    line-height: 19px;
  }

  & .rw-input {
    color: ${({ theme }) => theme.textColor};
  }

  & .rw-list-option:hover {
    background: ${({ theme }) => theme.greyColor20};
  }

  & .rw-list-option.rw-state-selected {
    background: ${({ theme }) => theme.primaryColor12};
    color: ${({ theme }) => theme.primaryColor};
  }

  &.rw-state-focus {
    & > .rw-widget-container {
      border: 1px solid ${({ theme }) => theme.primaryColor};
      box-shadow: none;
      background: ${({ theme }) => theme.primaryColor12};
    }

    & .rw-btn {
      color: ${({ theme }) => theme.primaryColor};
    }
  }

  & .withButton,
  &.rw-state-focus .withButton {
    border: 1px solid ${props => props.theme.primaryColor};
    outline: none;
    border-radius: 4px;
    padding: 5px 10px 6px;
    font-weight: 500;
    font-size: 12px;
    line-height: 15px;
    text-align: center;
    letter-spacing: 0.03em;
    cursor: pointer;
    color: ${props => props.theme.whiteColor};
    background: ${props => props.theme.primaryColor};
    text-decoration: none;
    min-width: 130px;
    height: 28px;

    &:hover {
      box-shadow: 0 1px 3px rgba(53, 53, 66, 0.2),
        0 1px 2px rgba(53, 53, 66, 0.12), 0 1px 1px rgba(53, 53, 66, 0.14);
      background: ${props => props.theme.primaryColor};
      border: 1px solid ${props => props.theme.primaryColor};
    }
    & .rw-input,
    & .rw-placeholder {
      padding: 0;
      color: ${props => props.theme.whiteColor};
    }
    & .rw-select {
      display: none;
    }
    & ~ .rw-popup-container {
      min-width: 260px;
      left: auto;
    }
  }
`;

const DropDown: React.FC<IProps> = props => {
  const formatMessage = useIntl().formatMessage;

  return (
    <StyledDropdownList
      withBorder={props.withBorder}
      containerClassName={props.withButton ? "withButton" : ""}
      filter={props.hasFilter ? "contains" : false}
      placeholder={
        props.withButton ? props.textButton : props.placeholder || "..."
      }
      data={props.data}
      messages={{
        filterPlaceholder: props.filterPlaceholder || "",
        emptyFilter: formatMessage({
          id: "form.noResult"
        })
      }}
      textField="text"
      valueField="value"
      value={props.value}
      disabled={props.disabled}
      valueComponent={({ item }: { item: IDataItem }) =>
        props.withButton ? (
          <WithButtonItem text={props.textButton} />
        ) : (
          <ValueInput item={item} />
        )
      }
      itemComponent={ListItem}
      onSelect={props.onSelect}
      // @ts-ignore
      searchIcon=""
    />
  );
};

export default DropDown;
