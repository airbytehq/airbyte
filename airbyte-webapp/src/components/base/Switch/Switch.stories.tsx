import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Switch } from "./Switch";

export default {
  title: "Ui/Switch",
  component: Switch,
  argTypes: {},
} as ComponentMeta<typeof Switch>;

const Template: ComponentStory<typeof Switch> = (args) => <Switch {...args} />;

export const StatusIcon = Template.bind({});
StatusIcon.args = {
  checked: false,
};
