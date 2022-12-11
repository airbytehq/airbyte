import { ComponentStory, ComponentMeta } from "@storybook/react";

import { TextArea } from "./TextArea";

export default {
  title: "Ui/TextArea",
  component: TextArea,
} as ComponentMeta<typeof TextArea>;

const Template: ComponentStory<typeof TextArea> = (args) => <TextArea {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  placeholder: "Enter text here...",
};
