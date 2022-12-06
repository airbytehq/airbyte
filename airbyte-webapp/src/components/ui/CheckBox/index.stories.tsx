import { ComponentStory, ComponentMeta } from "@storybook/react";
import { useState } from "react";

import { CheckBox } from ".";

export default {
  title: "UI/Checkbox",
  component: CheckBox,
  argTypes: {},
} as ComponentMeta<typeof CheckBox>;

const Template: ComponentStory<typeof CheckBox> = (args) => {
  const [checked, setChecked] = useState(false);
  return <CheckBox {...args} checked={checked} onClick={() => setChecked((s) => !s)} />;
};
export const Primary = Template.bind({});
Primary.args = {
  checked: false,
};
