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
  disabled: false,
};

export const LoadingButton = Template.bind({});
LoadingButton.args = {
  variant: "primary",
  children: "Primary",
  isLoading: true,
  disabled: false,
};

export const ButtonWithIcon = Template.bind({});
ButtonWithIcon.args = {
  variant: "primary",
  icon: <FontAwesomeIcon icon={faTimes} />,
  iconPosition: "left",
  disabled: false,
};

export const ButtonWithTextAndIconLeft = Template.bind({});
ButtonWithTextAndIconLeft.args = {
  variant: "primary",
  icon: <FontAwesomeIcon icon={faTimes} />,
  iconPosition: "left",
  children: "Icon Left",
  disabled: false,
};

export const ButtonWithTextAndIconRight = Template.bind({});
ButtonWithTextAndIconRight.args = {
  variant: "primary",
  icon: <FontAwesomeIcon icon={faTimes} />,
  iconPosition: "right",
  children: "Icon Right",
  disabled: false,
};

export const Secondary = Template.bind({});
Secondary.args = {
  variant: "secondary",
  children: "Secondary",
  disabled: false,
};

export const Light = Template.bind({});
Light.args = {
  variant: "light",
  children: "Light",
  disabled: false,
};

export const Danger = Template.bind({});
Danger.args = {
  variant: "danger",
  children: "Danger",
  disabled: false,
};

export const Clear = Template.bind({});
Clear.args = {
  variant: "clear",
  children: "No Stroke",
  disabled: false,
};

export const Dark = Template.bind({});
Dark.args = {
  variant: "dark",
  children: "Dark",
  disabled: false,
};
