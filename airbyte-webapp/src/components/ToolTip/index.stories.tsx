import { ComponentStory, ComponentMeta } from "@storybook/react";

import ToolTip from "./ToolTip";

export default {
  title: "Ui/ToolTip",
  component: ToolTip,
  argTypes: {
    control: { type: { name: "string", required: true } },
    children: { type: { name: "string", required: true } },
  },
} as ComponentMeta<typeof ToolTip>;

const Template: ComponentStory<typeof ToolTip> = (args) => <ToolTip {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  control: "Hover to see ToolTip",
  children: "Here's a tip for you!",
};
