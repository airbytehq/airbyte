import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Icon } from "./Icon";

export default {
  title: "Ui/Icon",
  component: Icon,
} as ComponentMeta<typeof Icon>;

const Template: ComponentStory<typeof Icon> = (args) => <Icon {...args} />;

export const ArrowRightIcon = Template.bind({});
ArrowRightIcon.args = {
  type: "arrowRight",
};
