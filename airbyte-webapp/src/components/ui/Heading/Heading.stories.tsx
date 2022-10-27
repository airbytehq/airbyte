import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Heading } from "./Heading";

export default {
  title: "Ui/Heading",
  component: Heading,
} as ComponentMeta<typeof Heading>;

const Template: ComponentStory<typeof Heading> = (args) => <Heading {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  size: "md",
  children:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
};
