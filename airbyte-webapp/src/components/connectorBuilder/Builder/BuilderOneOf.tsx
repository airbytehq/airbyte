import { useField } from "formik";
import React from "react";

import GroupControls from "components/GroupControls";
import { ControlLabels } from "components/LabeledControl";
import { DropDown } from "components/ui/DropDown";

interface Option {
  label: string;
  value: string;
  default?: object;
}

interface OneOfOption {
  label: string; // label shown in the dropdown menu
  typeValue: string; // value to set on the `type` field for this component - should match the oneOf type definition
  default?: object; // default values for the path
  children?: React.ReactNode;
}

interface BuilderOneOfProps {
  options: OneOfOption[];
  path: string; // path to the oneOf component in the json schema
  label: string;
  tooltip: string;
}

export const BuilderOneOf: React.FC<BuilderOneOfProps> = ({ options, path, label, tooltip }) => {
  const [, , oneOfPathHelpers] = useField(path);
  const typePath = `${path}.type`;
  const [typePathField] = useField(typePath);
  const value = typePathField.value;

  const selectedOption = options.find((option) => option.typeValue === value);

  return (
    <GroupControls
      label={<ControlLabels label={label} infoTooltipContent={tooltip} />}
      dropdown={
        <DropDown
          {...typePathField}
          options={options.map((option) => {
            return { label: option.label, value: option.typeValue, default: option.default };
          })}
          value={value ?? options[0].typeValue}
          onChange={(selectedOption: Option) => {
            if (selectedOption.value === value) {
              return;
            }
            // clear all values for this oneOf and set selected option and default values
            oneOfPathHelpers.setValue({
              type: selectedOption.value,
              ...selectedOption.default,
            });
          }}
        />
      }
    >
      {selectedOption?.children}
    </GroupControls>
  );
};
