import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Toast } from "./Toast";

export default {
  title: "UI/Toast",
  component: Toast,
  argTypes: {
    title: { type: { name: "string", required: false } },
    text: { type: { name: "string", required: false } },
    onClose: { table: { disable: true } },
  },
} as ComponentMeta<typeof Toast>;

const Template: ComponentStory<typeof Toast> = (args) => <Toast {...args} />;

export const Basic = Template.bind({});
Basic.args = {
  text: "This is a basic card",
};

export const WithTitle = Template.bind({});
WithTitle.args = {
  title: "With Title",
  text: "This is a card with a title",
};

export const WithCloseButton = Template.bind({});
WithCloseButton.args = {
  title: "With Close button",
  text: "This is a card with a close button",
  onClose: () => {
    console.log("Closed!");
  },
};
