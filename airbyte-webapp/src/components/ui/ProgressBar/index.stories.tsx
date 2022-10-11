import { ComponentStory, ComponentMeta } from "@storybook/react";

import { ProgressBar } from "./ProgressBar";

export default {
  title: "UI/ProgressBar",
  component: ProgressBar,
  argTypes: {},
} as ComponentMeta<typeof ProgressBar>;

const Template: ComponentStory<typeof ProgressBar> = (args) => <ProgressBar {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  runTime: 10,
  text: "This is taking a long time...",
};
