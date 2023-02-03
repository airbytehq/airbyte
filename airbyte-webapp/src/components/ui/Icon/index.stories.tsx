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

export const CreditsIcon = Template.bind({});
CreditsIcon.args = {
  type: "credits",
};

export const CrossIcon = Template.bind({});
CrossIcon.args = {
  type: "cross",
};

export const DocsIcon = Template.bind({});
DocsIcon.args = {
  type: "docs",
};

export const GAIcon = Template.bind({});
GAIcon.args = {
  type: "ga",
};

export const InfoIcon = Template.bind({});
InfoIcon.args = {
  type: "info",
};

export const MinusIcon = Template.bind({});
MinusIcon.args = {
  type: "minus",
};

export const ModificationIcon = Template.bind({});
ModificationIcon.args = {
  type: "modification",
};

export const MoonIcon = Template.bind({});
MoonIcon.args = {
  type: "moon",
};

export const PauseIcon = Template.bind({});
PauseIcon.args = {
  type: "pause",
};

export const PencilIcon = Template.bind({});
PencilIcon.args = {
  type: "pencil",
};

export const PlayIcon = Template.bind({});
PlayIcon.args = {
  type: "play",
};

export const PlusIcon = Template.bind({});
PlusIcon.args = {
  type: "plus",
};

export const RotateIcon = Template.bind({});
RotateIcon.args = {
  type: "rotate",
};
