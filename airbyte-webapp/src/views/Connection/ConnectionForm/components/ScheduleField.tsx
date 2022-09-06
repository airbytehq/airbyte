import { Field, FieldInputProps, FieldProps } from "formik";
import { ChangeEvent, useMemo, useState } from "react";
import { useIntl } from "react-intl";

import { ControlLabels, DropDown, DropDownRow, Input } from "components";

import {
  ConnectionScheduleData,
  ConnectionScheduleDataBasicSchedule,
  ConnectionScheduleDataCron,
  ConnectionScheduleType,
} from "core/request/AirbyteClient";

import availableCronTimeZones from "../../../../config/availableCronTimeZones.json";
import { ConnectionFormMode } from "../ConnectionForm";
import { useFrequencyDropdownData } from "../formConfig";
import styles from "./ScheduleField.module.scss";

interface ScheduleFieldProps {
  scheduleData: ConnectionScheduleData | undefined;
  scheduleType: ConnectionScheduleType | undefined;
  mode: ConnectionFormMode;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  setFieldValue: (field: string, value: any, shouldValidate?: boolean | undefined) => void;
  onDropDownSelect?: (item: DropDownRow.IDataItem) => void;
}

const ScheduleField: React.FC<ScheduleFieldProps> = ({
  scheduleData,
  scheduleType,
  mode,
  setFieldValue,
  onDropDownSelect,
}) => {
  const [isCustomSchedule, setIsCustomSchedule] = useState<boolean>(scheduleType === ConnectionScheduleType.cron);
  const { formatMessage } = useIntl();
  const frequencies = useFrequencyDropdownData(scheduleData);

  const onScheduleChange = (
    item: DropDownRow.IDataItem,
    field: FieldInputProps<ConnectionScheduleDataBasicSchedule>
  ) => {
    onDropDownSelect?.(item);
    setFieldValue(field.name, item.value);

    // Also set scheduleType for yup validation
    const isManualOrCron = item.value === ConnectionScheduleType.manual || item.value === ConnectionScheduleType.cron;
    const scheduleType = isManualOrCron ? (item.value as ConnectionScheduleType) : ConnectionScheduleType.basic;

    setFieldValue("scheduleType", scheduleType);

    // Show cron and timezone fields based on the frequency
    if (item.value === ConnectionScheduleType.cron) {
      setIsCustomSchedule(true);
    } else {
      setIsCustomSchedule(false);
    }
  };

  const getBasicScheduleValue = (value: ConnectionScheduleDataBasicSchedule) => {
    // To set the initial value for the frequency dropdown. Only for Manual and Custom
    if (!value) {
      if (scheduleType === ConnectionScheduleType.cron) {
        return formatMessage({
          id: "frequency.cron",
        }).toLowerCase();
      }

      return formatMessage({
        id: "frequency.manual",
      }).toLowerCase();
    }

    return value;
  };

  const getZoneValue = (currentSelectedZone: string) => {
    if (!currentSelectedZone) {
      return cronTimeZones[0].value;
    }

    return currentSelectedZone;
  };

  const onCronInputChange = (
    event: ChangeEvent<HTMLInputElement>,
    field: FieldInputProps<ConnectionScheduleDataCron>
  ) => {
    setFieldValue(field.name, {
      ...field.value,
      cronExpression: event.currentTarget.value,
    });
  };

  const onCronZoneChange = (event: DropDownRow.IDataItem, field: FieldInputProps<ConnectionScheduleDataCron>) => {
    setFieldValue(field.name, {
      ...field.value,
      cronTimeZone: event.value,
    });
  };

  const cronTimeZones = useMemo(() => {
    return availableCronTimeZones.map((zone: string) => ({ label: zone, value: zone }));
  }, []);

  return (
    <>
      <Field name="scheduleData.basicSchedule">
        {({ field, meta }: FieldProps<ConnectionScheduleDataBasicSchedule>) => (
          <div className={styles.flexRow}>
            <div className={styles.leftFieldCol}>
              <ControlLabels
                className={styles.connectorLabel}
                nextLine
                error={!!meta.error && meta.touched}
                label={formatMessage({
                  id: "form.frequency",
                })}
                message={formatMessage({
                  id: "form.frequency.message",
                })}
              />
            </div>
            <div className={styles.rightFieldCol} style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
              <DropDown
                {...field}
                error={!!meta.error && meta.touched}
                options={frequencies}
                onChange={(item) => {
                  onScheduleChange(item, field);
                }}
                value={getBasicScheduleValue(field.value)}
              />
            </div>
          </div>
        )}
      </Field>
      {isCustomSchedule && (
        <Field name="scheduleData.cron">
          {({ field, meta }: FieldProps<ConnectionScheduleDataCron>) => (
            <div className={styles.flexRow}>
              <div className={styles.leftFieldCol}>
                <ControlLabels
                  className={styles.connectorLabel}
                  nextLine
                  error={!!meta.error && meta.touched}
                  label={formatMessage({
                    id: "form.cronExpression",
                  })}
                />
              </div>
              <div className={styles.rightFieldCol} style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
                <div className={styles.flexRow}>
                  <Input
                    disabled={mode === "readonly"}
                    error={!!meta.error}
                    data-testid="cronExpression"
                    onBlur={field.onBlur}
                    placeholder={formatMessage({
                      id: "form.cronExpression.placeholder",
                    })}
                    value={field.value?.cronExpression}
                    onChange={(event: ChangeEvent<HTMLInputElement>) => onCronInputChange(event, field)}
                  />
                  <DropDown
                    className={styles.cronZonesDropdown}
                    options={cronTimeZones}
                    value={getZoneValue(field.value?.cronTimeZone)}
                    onBlur={field.onBlur}
                    onChange={(item: DropDownRow.IDataItem) => onCronZoneChange(item, field)}
                  />
                </div>
              </div>
            </div>
          )}
        </Field>
      )}
    </>
  );
};

export default ScheduleField;
