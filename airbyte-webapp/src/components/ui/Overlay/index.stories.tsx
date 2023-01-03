import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Overlay } from "./Overlay";

export default {
  title: "UI/Overlay",
  component: Overlay,
  argTypes: {},
} as ComponentMeta<typeof Overlay>;

const Template: ComponentStory<typeof Overlay> = (args) => <Overlay {...args} />;

export const Primary = Template.bind({});
Primary.args = {};
