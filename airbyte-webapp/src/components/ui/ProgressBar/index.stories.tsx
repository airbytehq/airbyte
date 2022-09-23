import { ComponentStory, ComponentMeta } from "@storybook/react";

import { ProgressBar } from "./ProgressBar";

export default {
  title: "UI/ProgressBar",
  component: ProgressBar,
  argTypes: {},
} as ComponentMeta<typeof ProgressBar>;

const Template: ComponentStory<typeof ProgressBar> = (args) => <ProgressBar {...args} />;

export const Primary = Template.bind({
  text: "Text...",
  runTime: 50,
});
