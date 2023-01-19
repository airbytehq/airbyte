import { action } from "@storybook/addon-actions";
import { ComponentMeta } from "@storybook/react";
import { ChangeEvent, useState } from "react";

import { CheckBox, CheckBoxProps } from "./CheckBox";

export default {
  title: "Ui/CheckBox",
  component: CheckBox,
  argTypes: {
    disabled: { control: "boolean" },
    checked: { control: "boolean" },
    indeterminate: { control: "boolean" },
    elSize: {
      options: ["lg", "sm"],
      control: { type: "radio" },
    },
  },
} as ComponentMeta<typeof CheckBox>;

const CheckBoxWithState = ({ checked: initial = false, ...props }: CheckBoxProps) => {
  const [checked, setChecked] = useState(initial);
  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    action("Checkbox clicked")(event);
    setChecked((prev) => !prev);
  };
  return <CheckBox {...props} checked={checked} onChange={handleChange} />;
};

export const Base = (args: CheckBoxProps) => <CheckBoxWithState {...args} />;

Base.args = {};

export const Checked = (args: CheckBoxProps) => <CheckBoxWithState {...args} />;

Checked.args = {
  checked: true,
};

export const CheckedSmall = (args: CheckBoxProps) => <CheckBoxWithState {...args} />;

CheckedSmall.args = {
  checked: true,
  elSize: "sm",
};

export const Disabled = (args: CheckBoxProps) => <CheckBoxWithState {...args} />;

Disabled.args = {
  disabled: true,
};

export const DisabledChecked = (args: CheckBoxProps) => <CheckBoxWithState {...args} />;

DisabledChecked.args = {
  disabled: true,
  checked: true,
};

export const Indeterminate = (args: CheckBoxProps) => <CheckBoxWithState {...args} />;

Indeterminate.args = {
  indeterminate: true,
};

export const IndeterminateDisabled = (args: CheckBoxProps) => <CheckBoxWithState {...args} />;

IndeterminateDisabled.args = {
  indeterminate: true,
  disabled: true,
};
