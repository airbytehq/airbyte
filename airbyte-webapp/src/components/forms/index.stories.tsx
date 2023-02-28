import { StoryObj } from "@storybook/react";
import * as yup from "yup";

import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { FlexContainer, FlexItem } from "components/ui/Flex";

import { RHFForm, RHFControl } from "./index";

const schema = yup.object({
  some_input: yup.string().required("This is a required field."),
  some_password: yup.string().min(5, "The password needs to be at least 5 characters long."),
  some_date: yup.string().required("This is a required field."),
  some_select: yup.string().required("This is a required field."),
});

export default {
  title: "Forms",
  component: RHFForm,
  parameters: { actions: { argTypesRegex: "^on.*" } },
} as StoryObj<typeof RHFForm>;

interface MyFormValues {
  some_input: string;
  some_password: string;
  some_date: string;
  some_select: string | undefined;
}

const defaultValues: MyFormValues = {
  some_input: "",
  some_password: "3mnv0dkln2%#@9fds",
  some_date: "",
  some_select: undefined,
};

const listOptions = ["one", "two", "three"].map((v) => ({ label: v, value: v }));

const MyFormControl = RHFControl<MyFormValues>;

export const Primary: StoryObj<typeof RHFForm> = {
  render: (props) => (
    <RHFForm {...props} schema={schema} defaultValues={defaultValues}>
      <Card withPadding>
        <RHFControl<MyFormValues>
          fieldType="input"
          name="some_input"
          label="A default text input"
          description="Some default message that appears under the label"
        />
        <MyFormControl
          fieldType="input"
          type="password"
          name="some_password"
          label="Password input"
          labelTooltip={
            <>
              <p>A tooltip to give the user more context. Can also include HTML:</p>
              <ol>
                <li>One</li>
                <li>Two</li>
                <li>Three</li>
              </ol>
            </>
          }
        />
        <MyFormControl fieldType="date" name="some_date" format="date-time" label="Date input" />
        <MyFormControl fieldType="dropdown" name="some_select" label="DropDown input" options={listOptions} />
        <FlexContainer justifyContent="flex-end">
          <FlexItem>
            <Button type="submit">Submit</Button>
          </FlexItem>
        </FlexContainer>
      </Card>
    </RHFForm>
  ),
};
