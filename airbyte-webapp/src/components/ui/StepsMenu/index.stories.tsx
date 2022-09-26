import { ComponentStory, ComponentMeta } from "@storybook/react";

import { StepsMenu } from "./StepsMenu";

export default {
  title: "UI/StepsMenu",
  component: StepsMenu,
  argTypes: {},
} as ComponentMeta<typeof StepsMenu>;

const Template: ComponentStory<typeof StepsMenu> = (args) => <StepsMenu {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  data: [
    {
      id: "status",
      name: "Status",
    },
    {
      id: "replication",
      name: "Replication",
    },
    {
      id: "transformation",
      name: "Transformation",
    },
  ],
  activeStep: "replication",
};
