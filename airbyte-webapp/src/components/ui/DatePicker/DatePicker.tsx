import { faCalendarAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import dayjs from "dayjs";
import React, { useCallback, useMemo } from "react";
import ReactDatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useIntl } from "react-intl";

import { Button } from "../Button";
import { Input } from "../Input";
import styles from "./DatePicker.module.scss";

/**
 * Converts a UTC dayjs object into a JS Date object with the same local time
 *
 * Necessary because react-datepicker does not allow us to set the timezone to UTC, only the current browser time.
 * In order to display the UTC timezone in the datepicker, we need to convert it into the local time:
 *
 * 2022-01-01T09:00:00Z       - the UTC format that airbyte-server expects (e.g. 9:00am)
 * 2022-01-01T10:00:00+01:00  - what react-datepicker might convert this date into and display (e.g. 10:00am - bad!)
 * 2022-01-01T09:00:00+01:00  - what we give react-datepicker instead, to trick it (User sees 9:00am - good!)
 */
export const toEquivalentLocalTimeInBrowserTimezone = (date: dayjs.Dayjs): Date => {
  // First, get the user's UTC offset based on the local time
  const browserUtcOffset = dayjs().utcOffset();

  // Convert the selected date into a string which we can use to initialize a new date object.
  // The second parameter to utcOffset() keeps the same local time, only changing the timezone.
  const dateInUtcAsString = date.utcOffset(browserUtcOffset, true).format();

  // Now we can return a JS date object in the user's timezone with the same local time as the UTC date
  return dayjs(dateInUtcAsString).toDate();
};

interface DatePickerProps {
  error?: boolean;
  value: string;
  onChange: (value: string) => void;
  withTime?: boolean;
  disabled?: boolean;
  onBlur?: (ev: React.FocusEvent<HTMLInputElement>) => void;
}

interface DatePickerButtonTriggerProps {
  onClick?: () => void;
}

const DatepickerButton = React.forwardRef<HTMLButtonElement, DatePickerButtonTriggerProps>((_props, ref) => {
  const { formatMessage } = useIntl();

  return (
    <Button
      className={styles.datepickerButton}
      aria-label={formatMessage({ id: "form.openDatepicker" })}
      onClick={_props.onClick}
      ref={ref}
      type="button"
      variant="clear"
      icon={<FontAwesomeIcon icon={faCalendarAlt} className={styles.dropdownButton} fixedWidth />}
    />
  );
});

export const DatePicker: React.FC<DatePickerProps> = ({
  disabled,
  onChange,
  onBlur,
  value = "",
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

  const onInputChanged = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  const dateValue = useMemo(() => (value ? dayjs.utc(value) : undefined), [value]);

  return (
    <div className={styles.wrapper}>
      <Input error={error} value={value} onChange={onInputChanged} onBlur={onBlur} />
      <div className={styles.datepickerButtonContainer}>
        <ReactDatePicker
          showPopperArrow={false}
          showTimeSelect={withTime}
          disabled={disabled}
          selected={dateValue?.isValid() ? toEquivalentLocalTimeInBrowserTimezone(dateValue) : undefined}
          onChange={onDateChanged}
          onBlur={onBlur}
          value={value}
          customInput={<DatepickerButton />}
          popperClassName={styles.popup}
        />
      </div>
    </div>
  );
};
