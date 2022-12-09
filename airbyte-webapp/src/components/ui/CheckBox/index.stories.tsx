import { ComponentMeta, ComponentStory } from "@storybook/react";

import { CheckBox } from "./CheckBox";
import docs from "./Checkbox.docs.mdx";

export default {
  title: "Ui/CheckBox",
  component: CheckBox,
  parameters: {
    docs: { page: docs },
  },
  argTypes: {
    disabled: { control: "select" },
    checked: { control: "check" },
    indeterminate: { control: "boolean" },
    small: { control: "boolean" },
  },
} as ComponentMeta<typeof CheckBox>;

const Template: ComponentStory<typeof CheckBox> = (args) => <CheckBox {...args} />;

export const Default = Template.bind({});
Default.args = {
  onChange: () => console.log("Clicked"),
};
