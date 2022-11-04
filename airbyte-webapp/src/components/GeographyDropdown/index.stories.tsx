import { ComponentStory, ComponentMeta } from "@storybook/react";

import { GeographyDropdown } from "./GeographyDropdown";

export default {
  title: "Common/GeographyDropdown",
  component: GeographyDropdown,
} as ComponentMeta<typeof GeographyDropdown>;

const Template: ComponentStory<typeof GeographyDropdown> = (args) => <GeographyDropdown {...args} />;

export const Empty = Template.bind({});
Empty.args = {};

export const Primary = Template.bind({});
Primary.args = {
  options: [
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
  ],
};
