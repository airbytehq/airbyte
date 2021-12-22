import React from "react";
import { Props } from "react-select";
import { SelectComponentsConfig } from "react-select/src/components";
import { CSSObject } from "styled-components";

import DropdownIndicator from "./components/DropdownIndicator";
import Menu from "./components/Menu";
import SingleValue from "./components/SingleValue";
import Option, { IDataItem } from "./components/Option";

import { equal, naturalComparatorBy } from "utils/objects";
import { SelectContainer } from "./SelectContainer";
import { CustomSelect } from "./CustomSelect";

export type OptionType = any;
type DropdownProps = Props<OptionType> & {
  withBorder?: boolean;
  fullText?: boolean;
  error?: boolean;
};

const DropDown: React.FC<DropdownProps> = React.forwardRef((props, ref) => {
  const propsComponents = props.components;

  const components = React.useMemo<SelectComponentsConfig<OptionType, boolean>>(
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
      } as any),
    [propsComponents]
  );

  const currentValue = props.isMulti
    ? props.options?.filter((op) =>
        props.value.find((o: OptionType) => equal(o, op.value))
      )
    : props.options?.find((op) => equal(op.value, props.value));

  const styles = {
    ...(props.styles ?? {}),
    menuPortal: (base: CSSObject, menuPortalProps: any) => ({
      ...(props.styles?.menuPortal?.(base, menuPortalProps) ?? { ...base }),
      zIndex: 9999,
    }),
  };

  return (
    <CustomSelect
      ref={ref}
      data-testid={props.name}
      $error={props.error}
      className="react-select-container"
      classNamePrefix="react-select"
      menuPortalTarget={document.body}
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
});

const defaultDataItemSort = naturalComparatorBy<IDataItem>(
  (dataItem) => dataItem.label || ""
);

export default DropDown;
export { DropDown, defaultDataItemSort };
export type { DropdownProps };
