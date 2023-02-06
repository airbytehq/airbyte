import { ComponentMeta, ComponentStory } from "@storybook/react";

import { RadioButton } from "./RadioButton";

export default {
  title: "Ui/RadioButton",
  component: RadioButton,
  argTypes: {
    disabled: { control: "boolean" },
    checked: { control: "boolean" },
  },
} as ComponentMeta<typeof RadioButton>;

const Template: ComponentStory<typeof RadioButton> = (args) => <RadioButton {...args} />;

export const Default = Template.bind({});
Default.args = {};
