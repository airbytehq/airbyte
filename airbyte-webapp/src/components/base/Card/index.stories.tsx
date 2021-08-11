import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Card } from "./Card";

export default {
  title: "Example/Card",
  component: Card,
} as ComponentMeta<typeof Card>;

const Template: ComponentStory<typeof Card> = (args) => <Card {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  children: "Text",
};
