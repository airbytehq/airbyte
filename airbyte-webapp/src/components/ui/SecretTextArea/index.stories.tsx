import { ComponentStory, ComponentMeta } from "@storybook/react";

import { SecretTextArea } from "./SecretTextArea";

export default {
  title: "UI/SecretTextArea",
  component: SecretTextArea,
  argTypes: {
    value: { control: { type: { name: "text", required: false } } },
    rows: { control: { type: { name: "number", required: false } } },
  },
} as ComponentMeta<typeof SecretTextArea>;

const Template: ComponentStory<typeof SecretTextArea> = (args) => (
  <SecretTextArea
    {...args}
    onChange={() => {
      // eslint-disable-next-line @typescript-eslint/no-empty-function
    }}
  />
);

export const Primary = Template.bind({});
Primary.args = {
  rows: 1,
  value: "testing",
};
