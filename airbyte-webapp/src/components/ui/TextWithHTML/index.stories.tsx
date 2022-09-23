import { ComponentStory, ComponentMeta } from "@storybook/react";

import { TextWithHTML } from "./TextWithHTML";

export default {
  title: "UI/TextWithHTML",
  component: TextWithHTML,
  argTypes: {},
} as ComponentMeta<typeof TextWithHTML>;

const Template: ComponentStory<typeof TextWithHTML> = (args) => <TextWithHTML {...args} />;

export const Primary = Template.bind({});
