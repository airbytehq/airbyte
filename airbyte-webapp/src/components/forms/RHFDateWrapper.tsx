import type { OmittableProperties, RHFDatePickerProps } from "./RHFControl";

import { Controller, useFormContext } from "react-hook-form";

import DatePicker from "components/ui/DatePicker";

import { FormValues } from "./RHFForm";

export const RHFDateWrapper = <T extends FormValues>({
  name,
  format = "date",
  hasError,
}: Omit<RHFDatePickerProps<T>, OmittableProperties>) => {
  const { control } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <DatePicker value={field.value} onChange={field.onChange} withTime={format === "date-time"} error={hasError} />
      )}
    />
  );
};
