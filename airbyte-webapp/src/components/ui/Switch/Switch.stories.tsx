import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Switch } from "./Switch";

export default {
  title: "Ui/Switch",
  component: Switch,
  argTypes: {},
} as ComponentMeta<typeof Switch>;

const Template: ComponentStory<typeof Switch> = (args) => <Switch {...args} />;

export const SwitchControl = Template.bind({});
SwitchControl.args = {
  checked: false,
  size: "sm",
  loading: false,
};
