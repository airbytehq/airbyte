import { faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { ComponentStory, ComponentMeta } from "@storybook/react";

import { Button } from "./Button";

export default {
  title: "UI/Button",
  component: Button,
  argTypes: {
    backgroundColor: { control: "color" },
  },
} as ComponentMeta<typeof Button>;

const Template: ComponentStory<typeof Button> = (args) => <Button {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  variant: "primary",
  children: "Primary",
  icon: <FontAwesomeIcon icon={faTimes} />,
  iconPosition: "left",
};

export const LoadingButton = Template.bind({});
LoadingButton.args = {
  variant: "primary",
  children: "Primary",
  isLoading: true,
};

export const ButtonWithIcon = Template.bind({});
ButtonWithIcon.args = {
  variant: "primary",
  icon: <FontAwesomeIcon icon={faTimes} />,
  iconPosition: "left",
};

export const ButtonWithTextAndIconLeft = Template.bind({});
ButtonWithTextAndIconLeft.args = {
  variant: "primary",
  icon: <FontAwesomeIcon icon={faTimes} />,
  iconPosition: "left",
  children: "Icon Left",
};

export const ButtonWithTextAndIconRight = Template.bind({});
ButtonWithTextAndIconRight.args = {
  variant: "primary",
  icon: <FontAwesomeIcon icon={faTimes} />,
  iconPosition: "right",
  children: "Icon Right",
};

export const Secondary = Template.bind({});
Secondary.args = {
  variant: "secondary",
  children: "Secondary",
};

export const Light = Template.bind({});
Light.args = {
  variant: "light",
  children: "Light",
};

export const Danger = Template.bind({});
Danger.args = {
  variant: "danger",
  children: "Danger",
};

export const Clear = Template.bind({});
Clear.args = {
  variant: "clear",
  children: "No Stroke",
};

export const Dark = Template.bind({});
Dark.args = {
  variant: "dark",
  children: "Dark",
};
