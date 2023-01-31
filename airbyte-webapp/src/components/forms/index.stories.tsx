import { ComponentStory, ComponentMeta } from "@storybook/react";
import { useForm, FormProvider } from "react-hook-form";

import { RHFControl } from "./index";

const RHF: React.FC = () => {
  const methods = useForm({ defaultValues: { test2: "test2 default", test3: "test3 also default" } });
  const onSubmit = (values: Record<string, string>) => {
    alert(JSON.stringify(values));
  };

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
  argTypes: {},
} as ComponentMeta<typeof RHF>;

const Template: ComponentStory<typeof RHF> = (args) => <RHF {...args} />;

export const Primary = Template.bind({});
Primary.args = {};
