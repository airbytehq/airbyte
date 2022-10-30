import { ComponentStory, ComponentMeta } from "@storybook/react";

import { GeographyDropdown } from "./GeographyDropdown";

export const defaultOptions = [
  {
    value: "us",
    label: "us",
  },
  {
    value: "auto",
    label: "auto",
  },
  {
    value: "eu",
    label: "eu",
  },
];

export default {
  title: "Ui/GeographyDropdown",
  component: GeographyDropdown,
} as ComponentMeta<typeof GeographyDropdown>;

const Template: ComponentStory<typeof GeographyDropdown> = (args) => <GeographyDropdown {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  options: defaultOptions,
};
