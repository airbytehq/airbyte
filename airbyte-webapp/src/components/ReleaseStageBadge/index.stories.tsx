import { ComponentStory, ComponentMeta } from "@storybook/react";

import { ReleaseStageBadge } from "./ReleaseStageBadge";

export default {
  title: "UI/ReleaseStageBadge",
  component: ReleaseStageBadge,
  argTypes: {},
} as ComponentMeta<typeof ReleaseStageBadge>;

const Template: ComponentStory<typeof ReleaseStageBadge> = (args) => <ReleaseStageBadge {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  stage: "alpha",
};
