import { ComponentStory, ComponentMeta } from "@storybook/react";

import { NumberBadge } from "./NumberBadge";

export default {
  title: "UI/NumberBadge",
  component: NumberBadge,
  argTypes: {},
} as ComponentMeta<typeof NumberBadge>;

const Template: ComponentStory<typeof NumberBadge> = (args) => <NumberBadge {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  value: 10,
};
