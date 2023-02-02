import { yupResolver } from "@hookform/resolvers/yup";
import { PropsWithChildren } from "react";
import { useForm, FormProvider } from "react-hook-form";
import { ObjectSchema } from "yup";

interface RHFFormProps {
  // todo: type values correctly
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onSubmit: (values: any) => Promise<unknown>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  schema: ObjectSchema<any>;
}

export const RHFForm: React.FC<PropsWithChildren<RHFFormProps>> = ({ children, onSubmit, schema }) => {
  const methods = useForm({
    defaultValues: { some_input: "Default input value", some_password: "Default password value" },
    resolver: yupResolver(schema),
    mode: "onBlur",
  });

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>{children}</form>
    </FormProvider>
  );
};
