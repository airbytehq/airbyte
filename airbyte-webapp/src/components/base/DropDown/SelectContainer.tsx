import React from "react";
import { components, ContainerProps } from "react-select";

import { OptionType } from "./DropDown";

export const SelectContainer: React.FC<
  ContainerProps<OptionType, false> & {
    selectProps: {
      "data-testid": string;
      role: string;
    };
  }
> = (props) => {
  const wrapperProps = {
    "data-testid": props.selectProps["data-testid"],
    role: props.selectProps.role || "combobox",
  };
  return <components.SelectContainer {...props} innerProps={{ ...props.innerProps, ...wrapperProps }} />;
};
