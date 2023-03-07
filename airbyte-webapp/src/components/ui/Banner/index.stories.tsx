import { ComponentStory, ComponentMeta } from "@storybook/react";

import { AlertBanner } from "./AlertBanner";

export default {
  title: "UI/AlertBanner",
  component: AlertBanner,
  argTypes: {},
} as ComponentMeta<typeof AlertBanner>;

const Template: ComponentStory<typeof AlertBanner> = (args) => <AlertBanner {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  message: "This is the AlertBanner component!",
};
