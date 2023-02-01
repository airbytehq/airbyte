import { ComponentStory, ComponentMeta } from "@storybook/react";
import { useForm, FormProvider } from "react-hook-form";

import { RHFControl } from "./index";

interface RHFProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onSubmit: (values: any) => void;
}

const RHF: React.FC<RHFProps> = ({ onSubmit }) => {
  const methods = useForm({
    defaultValues: { some_input: "Default input value", some_password: "Default password value" },
  });

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        <RHFControl fieldType="input" name="some_input" />
        <RHFControl fieldType="input" type="password" name="some_password" />
        <RHFControl fieldType="date" name="some_date" format="date-time" />
        <button type="submit">Submit</button>
      </form>
    </FormProvider>
  );
};

export default {
  title: "UI/Forms",
  component: RHF,
  argTypes: {
    onSubmit: { action: "submitted" },
  },
} as ComponentMeta<typeof RHF>;

const Template: ComponentStory<typeof RHF> = (args) => <RHF {...args} />;

export const Primary = Template.bind({});
Primary.args = {};
