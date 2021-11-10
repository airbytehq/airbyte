import { ComponentStory, ComponentMeta } from "@storybook/react";

import ContentCard from "./ContentCard";

export default {
  title: "Ui/ContentCard",
  component: ContentCard,
} as ComponentMeta<typeof ContentCard>;

const Template: ComponentStory<typeof ContentCard> = (args) => (
  <ContentCard {...args} />
);

export const Primary = Template.bind({});
Primary.args = {
  children: "Text",
  title: "Title",
};
