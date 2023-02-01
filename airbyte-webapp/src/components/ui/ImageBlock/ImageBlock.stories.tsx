import { ComponentStory, ComponentMeta } from "@storybook/react";

import { ImageBlock } from "./ImageBlock";

export default {
  title: "UI/ImageBlock",
  component: ImageBlock,
  argTypes: {},
} as ComponentMeta<typeof ImageBlock>;

const Template: ComponentStory<typeof ImageBlock> = (args) => <ImageBlock {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  img: undefined,
  small: undefined,
};
