import type { OmittableProperties, RHFInputFieldProps } from "./RHFControl";

import { useFormContext } from "react-hook-form";

import { Input } from "components/ui/Input";

import { FormValues } from "./RHFForm";

export const RHFInputWrapper = <T extends FormValues>({
  name,
  type,
  hasError,
}: Omit<RHFInputFieldProps<T>, OmittableProperties>) => {
  const { register } = useFormContext();

  return <Input {...register(name)} name={name} type={type} error={hasError} />;
};
