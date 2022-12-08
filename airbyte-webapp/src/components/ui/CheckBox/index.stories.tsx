import { ComponentMeta, ComponentStory } from "@storybook/react";

import { CheckBox } from "./CheckBox";

export default {
  title: "Ui/CheckBox",
  component: CheckBox,
  argTypes: {
    disabled: { control: "boolean" },
    checked: { control: "boolean" },
    indeterminate: { control: "boolean" },
  },
} as ComponentMeta<typeof CheckBox>;

const Template: ComponentStory<typeof CheckBox> = (args) => <CheckBox {...args} />;

export const Default = Template.bind({});
Default.args = {};
