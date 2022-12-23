import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Input } from "./Input";

export default {
  title: "Ui/Input",
  component: Input,
  argTypes: {
    disabled: { control: "boolean" },
    type: { control: { type: "select", options: ["text", "number", "password"] } },
  },
} as ComponentMeta<typeof Input>;

const Template: ComponentStory<typeof Input> = (args) => <Input {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  placeholder: "Enter text here...",
};
