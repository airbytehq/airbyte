import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import { ComponentStory, ComponentMeta } from "@storybook/react";

import { InfoBox } from "./InfoBox";

export default {
  title: "UI/InfoBox",
  component: InfoBox,
  argTypes: {
    children: { type: "string", required: true },
  },
} as ComponentMeta<typeof InfoBox>;

const Template: ComponentStory<typeof InfoBox> = (args) => <InfoBox {...args} />;
export const Primary = Template.bind({});
Primary.args = {
  icon: faEnvelope,
  children: "Here is some info.",
};
