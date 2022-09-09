import { ComponentStory, ComponentMeta } from "@storybook/react";

import { SecretTextArea } from "./SecretTextArea";

export default {
  title: "Ui/SecretTextArea",
  component: SecretTextArea,
} as ComponentMeta<typeof SecretTextArea>;

const Template: ComponentStory<typeof SecretTextArea> = (args) => <SecretTextArea {...args} />;

export const Primary = Template.bind({});
Primary.args = {};
