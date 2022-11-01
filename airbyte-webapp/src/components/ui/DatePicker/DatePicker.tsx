import dayjs from "dayjs";
import React, { useCallback } from "react";
import ReactDatePicker from "react-datepicker";

import "react-datepicker/dist/react-datepicker.css";

import { Input } from "../Input";
import styles from "./DatePicker.module.scss";

/**
 * TODO: This def needs some explanation!
 */
const toDateAssumingUtcAsTimezone = (date: dayjs.Dayjs): Date => {
  return dayjs(date.utcOffset(dayjs().utcOffset(), true).format()).toDate();
};

interface DatePickerProps {
  error?: boolean;
  value: string;
  onChange: (value: string) => void;
  withTime?: boolean;
  disabled?: boolean;
  onBlur?: (ev: React.FocusEvent<HTMLInputElement>) => void;
}

export const DatePicker: React.FC<DatePickerProps> = ({
  disabled,
  onChange,
  onBlur,
  value,
  error,
  withTime = false,
}) => {
  const onDateChanged = useCallback(
    (val: Date | null) => {
      const date = dayjs(val);
      if (!date.isValid()) {
        onChange("");
        return;
      }

      const formattedDate = withTime ? date.utcOffset(0, true).format() : date.format("YYYY-MM-DD");
      onChange(formattedDate);
    },
    [onChange, withTime]
  );

  const dateValue = value ? dayjs.utc(value) : undefined;

  return (
    <ReactDatePicker
      showTimeSelect={withTime}
      isClearable
      disabled={disabled}
      selected={dateValue?.isValid() ? toDateAssumingUtcAsTimezone(dateValue) : undefined}
      onChange={onDateChanged}
      onBlur={onBlur}
      value={value}
      customInput={<Input error={error} />}
      clearButtonClassName={styles.clearButton}
      popperClassName={styles.popup}
    />
  );
};
