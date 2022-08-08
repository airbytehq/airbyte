import { ComponentStory, ComponentMeta } from "@storybook/react";

import { ImageBlock } from "./ImageBlock";

export default {
  title: "Ui/ImageBlock",
  component: ImageBlock,
  argTypes: {},
} as ComponentMeta<typeof ImageBlock>;

const Template: ComponentStory<typeof ImageBlock> = (args) => <ImageBlock {...args} />;

export const ImageBlockControl = Template.bind({});
ImageBlockControl.args = {
  img: undefined,
  num: undefined,
  small: undefined,
};
