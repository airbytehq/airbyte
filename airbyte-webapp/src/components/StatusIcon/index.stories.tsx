import { ComponentStory, ComponentMeta } from "@storybook/react";

import StatusIconComponent from "./StatusIcon";

export default {
  title: "Ui/StatusIcon",
  component: StatusIconComponent,
  argTypes: {},
} as ComponentMeta<typeof StatusIconComponent>;

const Template: ComponentStory<typeof StatusIconComponent> = (args) => <StatusIconComponent {...args} />;

export const StatusIcon = Template.bind({});
StatusIcon.args = {
  status: "success",
};
