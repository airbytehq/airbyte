import { ComponentMeta } from "@storybook/react";
import * as yup from "yup";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { FlexContainer, FlexItem } from "components/ui/Flex";

import { RHFForm, RHFControl } from "./index";

/**
 * todo:
 * - Add Dropdown control
 * - Add TS typing (see 'any' in RHFForm's props)
 */

const schema = yup.object({
  some_input: yup.string().required("This is a required field."),
  some_password: yup.string().min(5, "The password needs to be at least 5 characters long."),
});

export default {
  title: "Forms",
  component: RHFForm,
  argTypes: {
    onSubmit: { action: "submitted" },
  },
} as ComponentMeta<typeof RHFForm>;

interface MyFormValues {
  some_input: string;
  some_password: string;
  some_date: string;
}

const defaultValues: MyFormValues = {
  some_input: "asdf",
  some_password: "1234",
  some_date: "",
};

const MyFormControl = RHFControl<MyFormValues>;

export const Primary = () => (
  <RHFForm onSubmit={(values) => Promise.resolve(console.log(values))} schema={schema} defaultValues={defaultValues}>
    <Card withPadding>
      <RHFControl<MyFormValues>
        fieldType="input"
        name="some_input"
        label="A default text input"
        description="Some default message that appears under the label"
      />
      <MyFormControl fieldType="input" type="password" name="some_password" label="Password input" />
      <MyFormControl fieldType="date" name="some_date" format="date-time" label="Date input" />
      <FlexContainer justifyContent="flex-end">
        <FlexItem>
          <Button type="submit">Submit</Button>
        </FlexItem>
      </FlexContainer>
    </Card>
  </RHFForm>
);
