import { Controller, useFormContext } from "react-hook-form";

import { DropDown } from "components/ui/DropDown";

import { RHFDropDownProps, OmittableProperties } from "./RHFControl";
import { FormValues } from "./RHFForm";

export const RHFDropDownWrapper = <T extends FormValues>({
  hasError,
  name,
  ...props
}: Omit<RHFDropDownProps<T>, OmittableProperties>) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <DropDown {...props} onChange={({ value }) => field.onChange(value)} value={field.value} error={hasError} />
      )}
    />
  );
};
