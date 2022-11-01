import { ComponentStory, ComponentMeta } from "@storybook/react";

import { StatusIcon } from "./StatusIcon";

export default {
  title: "UI/StatusIcon",
  component: StatusIcon,
  argTypes: {
    value: { type: { name: "number", required: false } },
  },
} as ComponentMeta<typeof StatusIcon>;

const Template: ComponentStory<typeof StatusIcon> = (args) => <StatusIcon {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  status: "success",
};
