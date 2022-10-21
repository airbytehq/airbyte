import { ComponentStory, ComponentMeta } from "@storybook/react";

import { PillButton } from "./PillButton";

export default {
  title: "UI/PillButton",
  component: PillButton,
} as ComponentMeta<typeof PillButton>;

const Template: ComponentStory<typeof PillButton> = (args) => <PillButton {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  children: "Pill Button",
};
