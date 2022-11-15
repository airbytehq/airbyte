import { ComponentMeta, ComponentStory } from "@storybook/react";

import { StepsIndicator } from "./StepsIndicator";

export default {
  title: "UI/StepsIndicator",
  component: StepsIndicator,
  argTypes: {},
} as ComponentMeta<typeof StepsIndicator>;

const Template: ComponentStory<typeof StepsIndicator> = (args) => <StepsIndicator {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  steps: [
    {
      id: "source",
      name: "Create source",
    },
    {
      id: "destination",
      name: "Create destination",
    },
    {
      id: "connection",
      name: "Create connection",
    },
  ],
  activeStep: "destination",
};
