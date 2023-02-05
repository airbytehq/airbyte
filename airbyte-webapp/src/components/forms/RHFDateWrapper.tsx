import type { OmittableProperties, RHFDatePickerProps } from "./RHFControl";

import { Controller, useFormContext } from "react-hook-form";

import DatePicker from "components/ui/DatePicker";

export const RHFDateWrapper: React.FC<Omit<RHFDatePickerProps, OmittableProperties>> = ({
  name,
  format = "date",
  hasError,
}) => {
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
