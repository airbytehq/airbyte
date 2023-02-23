import { ComponentStory, ComponentMeta } from "@storybook/react";

import { CollapsibleCard } from "./CollapsibleCard";

export default {
  title: "UI/CollapsibleCard",
  component: CollapsibleCard,
} as ComponentMeta<typeof CollapsibleCard>;

const Template: ComponentStory<typeof CollapsibleCard> = (args) => <CollapsibleCard {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  title: "Card Title",
  children: "The collapsible content goes here.",
  collapsible: true,
  defaultCollapsedState: true,
};
