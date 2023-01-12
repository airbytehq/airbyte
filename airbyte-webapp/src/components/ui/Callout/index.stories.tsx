import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Callout } from "./Callout";

export default {
  title: "UI/Callout",
  component: Callout,
  argTypes: {
    children: { type: "string", required: true },
  },
} as ComponentMeta<typeof Callout>;

const Template: ComponentStory<typeof Callout> = (args) => <Callout {...args} />;
export const Primary = Template.bind({});
Primary.args = {
  icon: faEnvelope,
  children: "Here is some info.",
};
