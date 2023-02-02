import { ComponentStory, ComponentMeta } from "@storybook/react";
import * as yup from "yup";

import { RHFForm, RHFControl } from "./index";

/**
 * todo:
 * - Add RHHFForm component
 * - Add Dropdown control
 * - Style errors (optional)
 * - add labels (optional)
 */

const schema = yup.object({
  some_input: yup.string().required(),
  some_password: yup.string().min(5, "too short!"),
});

export default {
  title: "UI/Forms",
  component: RHFForm,
  argTypes: {
    onSubmit: { action: "submitted" },
  },
} as ComponentMeta<typeof RHFForm>;

const Template: ComponentStory<typeof RHFForm> = (args) => <RHFForm {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  schema,
  children: (
    <>
      <RHFControl fieldType="input" name="some_input" />
      <RHFControl fieldType="input" type="password" name="some_password" />
      <RHFControl fieldType="date" name="some_date" format="date-time" />
      <button type="submit">Submit</button>
    </>
  ),
};
