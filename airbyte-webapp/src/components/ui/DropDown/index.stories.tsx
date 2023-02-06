import { ComponentStory, ComponentMeta } from "@storybook/react";

import { DropDown } from "./DropDown";

const listOptions = [
  {
    label: "one",
    value: "value",
  },
  {
    label: "two",
    value: "value",
  },
  {
    label: "three",
    value: "value",
  },
];

export default {
  title: "Ui/DropDown",
  component: DropDown,
  argTypes: {
    options: listOptions,
  },
} as ComponentMeta<typeof DropDown>;

const Template: ComponentStory<typeof DropDown> = (args) => <DropDown {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  options: listOptions,
};
