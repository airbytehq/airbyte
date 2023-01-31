import type { RHFInputFieldProps } from "./RHFControl";

import { useFormContext } from "react-hook-form";

import { Input } from "components/ui/Input";

export const RHFInputWrapper: React.FC<Omit<RHFInputFieldProps, "fieldType">> = ({ name, type }) => {
  const { register } = useFormContext();

  return <Input {...register(name)} name={name} type={type} />;
};
