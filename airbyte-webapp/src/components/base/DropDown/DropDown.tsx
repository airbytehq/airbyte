import React from "react";
import { CSSObjectWithLabel, GroupBase, Props, SelectComponentsConfig, StylesConfig } from "react-select";
import Select from "react-select/dist/declarations/src/Select";

import { equal, naturalComparatorBy } from "utils/objects";

import { DropdownIndicator } from "./components/DropdownIndicator";
import Menu from "./components/Menu";
import Option, { IDataItem } from "./components/Option";
import SingleValue from "./components/SingleValue";
import { CustomSelect } from "./CustomSelect";
import { SelectContainer } from "./SelectContainer";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type OptionType = any;

export interface DropdownProps<T = unknown> extends Props<OptionType> {
  withBorder?: boolean;
  $withBorder?: boolean;
  fullText?: boolean;
  error?: boolean;
  selectProps?: T;
}

// eslint-disable-next-line react/function-component-definition
function DropDownInner<T = unknown>(
  props: DropdownProps<T>,
  ref: React.ForwardedRef<Select<unknown, boolean, GroupBase<unknown>>>
) {
  const propsComponents = props.components;

  const components = React.useMemo<SelectComponentsConfig<OptionType, boolean, GroupBase<unknown>>>(
    () =>
      ({
        DropdownIndicator,
        SelectContainer,
        Menu,
        Option,
        SingleValue,
        IndicatorSeparator: null,
        ClearIndicator: null,
        MultiValueRemove: null,
        ...(propsComponents ?? {}),
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any),
    [propsComponents]
  );

  // undefined value is assumed to mean that value was not selected
  const currentValue =
    props.value !== undefined
      ? props.isMulti
        ? props.options?.filter((op) => props.value.find((o: OptionType) => equal(o, op.value)))
        : props.options?.find((op) => equal(op.value, props.value))
      : null;

  const styles: StylesConfig = {
    ...(props.styles ?? {}),
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    menuPortal: (base: CSSObjectWithLabel, menuPortalProps: any) => ({
      ...(props.styles?.menuPortal?.(base, menuPortalProps) ?? { ...base }),
      zIndex: 9999,
    }),
  };
  return (
    <CustomSelect
      ref={ref}
      data-testid={props.name}
      $error={props.error}
      menuPlacement="auto"
      menuPosition="fixed"
      menuShouldBlockScroll
      className="react-select-container"
      classNamePrefix="react-select"
      placeholder="..."
      isSearchable={false}
      closeMenuOnSelect={!props.isMulti}
      hideSelectedOptions={false}
      {...props}
      styles={styles}
      value={currentValue ?? null}
      components={components}
    />
  );
}

export const defaultDataItemSort = naturalComparatorBy<IDataItem>((dataItem) => dataItem.label || "");

export const DropDown = React.forwardRef(DropDownInner);
