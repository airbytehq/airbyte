import { ComponentStory, ComponentMeta } from "@storybook/react";

import { SingletonCard } from "./SingletonCard";

export default {
  title: "Ui/SingletonCard",
  component: SingletonCard,
  argTypes: {
    title: { type: { name: "string", required: false } },
    text: { type: { name: "string", required: false } },
    onClose: { table: { disable: true } },
  },
} as ComponentMeta<typeof SingletonCard>;

const Template: ComponentStory<typeof SingletonCard> = (args) => <SingletonCard {...args} />;

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
