import { ComponentStory, ComponentMeta } from "@storybook/react";

import { ListBox } from "./ListBox";

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

const Footer = {
  label: "Request a new geography",
  value: "new geography",
  link: "/geography",
};

export default {
  title: "Ui/ListBox",
  component: ListBox,
  argTypes: {
    options: listOptions,
  },
} as ComponentMeta<typeof ListBox>;

const Template: ComponentStory<typeof ListBox> = (args) => <ListBox {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  options: listOptions,
  footer: Footer,
};
