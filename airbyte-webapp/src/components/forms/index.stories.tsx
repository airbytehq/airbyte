import { ComponentStory, ComponentMeta } from "@storybook/react";
import * as yup from "yup";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { FlexContainer, FlexItem } from "components/ui/Flex";

import { RHFForm, RHFControl } from "./index";

/**
 * todo:
 * - Add RHHFForm component
 * - Add Dropdown control
 * - Style errors (optional)
 * - add labels (optional)
 */

const schema = yup.object({
  some_input: yup.string().required("This is a required field."),
  some_password: yup.string().min(5, "The password needs to be at least 5 characters long."),
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
    <Card withPadding>
      <RHFControl
        fieldType="input"
        name="some_input"
        label="A default text input"
        description="Some default message that appears under the label"
      />
      <RHFControl fieldType="input" type="password" name="some_password" label="Password input" />
      <RHFControl fieldType="date" name="some_date" format="date-time" label="Date input" />
      <FlexContainer justifyContent="flex-end">
        <FlexItem>
          <Button type="submit">Submit</Button>
        </FlexItem>
      </FlexContainer>
    </Card>
  ),
};
