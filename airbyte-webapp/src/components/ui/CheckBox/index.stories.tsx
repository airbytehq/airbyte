import { ComponentStory, ComponentMeta } from "@storybook/react";
import { useState } from "react";

import { Checkbox } from "./Checkbox";

export default {
  title: "UI/Checkbox",
  component: Checkbox,
  argTypes: {},
} as ComponentMeta<typeof Checkbox>;

const Template: ComponentStory<typeof Checkbox> = (args) => {
  const [checked, setChecked] = useState(false);
  return <Checkbox {...args} checked={checked} onClick={() => setChecked((s) => !s)} />;
};
export const Primary = Template.bind({});
Primary.args = {
  checked: false,
};
