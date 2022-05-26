import { ComponentStory, ComponentMeta } from "@storybook/react";

import { HeadlessSwitch } from "./HeadlessSwitch";

export default {
  title: "Ui/HeadlessSwitch",
  component: HeadlessSwitch,
  argTypes: {},
} as ComponentMeta<typeof HeadlessSwitch>;

const Template: ComponentStory<typeof HeadlessSwitch> = (args) => <HeadlessSwitch {...args} />;

export const SwitchControl = Template.bind({});
SwitchControl.args = {
  checked: false,
  small: false,
  loading: false,
};
