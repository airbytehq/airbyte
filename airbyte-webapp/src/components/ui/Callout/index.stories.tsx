import { faEnvelope } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Callout } from "./Callout";
import { Text } from "../Text";

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
  children: (
    <>
      <FontAwesomeIcon icon={faEnvelope} size="lg" />
      <Text>"Here is some info."</Text>
    </>
  ),
};
