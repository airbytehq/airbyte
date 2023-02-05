import type { OmittableProperties, RHFInputFieldProps } from "./RHFControl";

import { useFormContext } from "react-hook-form";

import { Input } from "components/ui/Input";

export const RHFInputWrapper: React.FC<Omit<RHFInputFieldProps, OmittableProperties>> = ({ name, type, hasError }) => {
  const { register } = useFormContext();

  return <Input {...register(name)} name={name} type={type} error={hasError} />;
};
