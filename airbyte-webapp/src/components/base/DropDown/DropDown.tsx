import React from "react";
import styled from "styled-components";
import Select, { Props } from "react-select";

import DropdownIndicator from "./components/DropdownIndicator";
import Menu from "./components/Menu";
import SingleValue from "./components/SingleValue";
import Option, { IDataItem } from "./components/Option";

import { equal, naturalComparatorBy } from "utils/objects";
import { SelectComponentsConfig } from "react-select/src/components";

type OptionType = any;
type DropdownProps = Props<OptionType> & {
  withBorder?: boolean;
  fullText?: boolean;
  error?: boolean;
};

const CustomSelect = styled(Select)<{
  $withBorder?: boolean;
  $error?: boolean;
}>`
  & > .react-select__control {
    height: ${({ $withBorder }) => ($withBorder ? 31 : 36)}px;

    box-shadow: none;
    border: 1px solid
      ${({ theme, $withBorder, $error }) =>
        $error
          ? theme.dangerColor
          : $withBorder
          ? theme.greyColor30
          : theme.greyColor0};
    background: ${({ theme }) => theme.greyColor0};
    border-radius: 4px;
    font-size: 14px;
    line-height: 20px;
    min-height: 36px;

    &:hover {
      border-color: ${({ theme, $error }) =>
        $error ? theme.dangerColor : theme.greyColor20};
      background: ${({ theme }) => theme.greyColor20};
    }

    &.react-select__control--menu-is-open {
      border: 1px solid ${({ theme }) => theme.primaryColor};
      box-shadow: none;
      background: ${({ theme }) => theme.primaryColor12};
    }

    & .react-select__multi-value {
      background: rgba(255, 255, 255, 0);
    }

    & .react-select__value-container {
      overflow: visible;
    }
  }
`;

const DropDown: React.FC<DropdownProps> = (props) => {
  const propsComponents = props.components;

  const components = React.useMemo<SelectComponentsConfig<OptionType, boolean>>(
    () =>
      ({
        DropdownIndicator,
        Menu,
        Option,
        SingleValue,
        IndicatorSeparator: null,
        ClearIndicator: null,
        MultiValueRemove: null,
        ...(propsComponents ?? {}),
      } as any),
    [propsComponents]
  );

  const currentValue = props.isMulti
    ? props.options?.filter((op) =>
        props.value.find((o: any) => equal(o, op.value))
      )
    : props.options?.find((op) => equal(op.value, props.value));

  return (
    <CustomSelect
      data-testid={props.name}
      $error={props.error}
      className="react-select-container"
      classNamePrefix="react-select"
      menuPortalTarget={document.body}
      placeholder="..."
      isSearchable={false}
      closeMenuOnSelect={!props.isMulti}
      hideSelectedOptions={false}
      styles={{ menuPortal: (base: any) => ({ ...base, zIndex: 9999 }) }}
      {...props}
      value={currentValue}
      components={components}
    />
  );
};

const defaultDataItemSort = naturalComparatorBy<IDataItem>(
  (dataItem) => dataItem.label || ""
);

export default DropDown;
export { DropDown, defaultDataItemSort };
export type { DropdownProps };
