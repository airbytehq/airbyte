import { ComponentStory, ComponentMeta } from "@storybook/react";

import { InfoText } from "./InfoText";

export default {
  title: "UI/InfoText",
  component: InfoText,
} as ComponentMeta<typeof InfoText>;

const Template: ComponentStory<typeof InfoText> = (args) => (
  <div style={{ width: "300px" }}>
    <InfoText {...args} />
  </div>
);

export const InfoTextDefault = Template.bind({});
InfoTextDefault.args = {
  variant: "grey",
  children: "test",
};
