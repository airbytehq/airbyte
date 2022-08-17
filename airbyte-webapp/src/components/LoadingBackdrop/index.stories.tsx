import { ComponentStory, ComponentMeta } from "@storybook/react";

import { LoadingBackdrop } from "./LoadingBackdrop";

export default {
  title: "Ui/LoadingBackdrop",
  component: LoadingBackdrop,
  argTypes: {
    loading: { type: "boolean", required: true },
    small: { type: "boolean", required: false },
  },
} as ComponentMeta<typeof LoadingBackdrop>;

const Template: ComponentStory<typeof LoadingBackdrop> = (args) => (
  <div style={{ height: 200, width: 200, border: "1px solid blue" }}>
    <LoadingBackdrop {...args}>
      <div style={{ padding: 15 }}>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore
      </div>
    </LoadingBackdrop>
  </div>
);
export const Primary = Template.bind({});
