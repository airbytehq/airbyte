import { Field, FieldInputProps, FieldProps, FormikProps, useField } from "formik";
import { ChangeEvent, useCallback, useMemo } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { ControlLabels, Link } from "components";
import { DropDown, DropDownOptionDataItem } from "components/ui/DropDown";
import { FlexContainer } from "components/ui/Flex";
import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";

import availableCronTimeZones from "config/availableCronTimeZones.json";
import { Action, Namespace } from "core/analytics";
import { ConnectionScheduleData, ConnectionScheduleType } from "core/request/AirbyteClient";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { links } from "utils/links";

import { FormikConnectionFormValues, useFrequencyDropdownData } from "./formConfig";
import styles from "./ScheduleField.module.scss";

const CRON_DEFAULT_VALUE = {
  cronTimeZone: "UTC",
  // Fire at 12:00 PM (noon) every day
  cronExpression: "0 0 12 * * ?",
};

export const ScheduleField: React.FC = () => {
  const { formatMessage } = useIntl();
  const { connection, mode } = useConnectionFormService();
  const frequencies = useFrequencyDropdownData(connection.scheduleData);
  const analyticsService = useAnalyticsService();

  const onDropDownSelect = useCallback(
    (item: DropDownOptionDataItem | null) => {
      const enabledStreams = connection.syncCatalog.streams.filter((stream) => stream.config?.selected).length;

      if (item) {
        analyticsService.track(Namespace.CONNECTION, Action.FREQUENCY, {
          actionDescription: "Frequency selected",
          frequency: item.label,
          connector_source_definition: connection.source.sourceName,
          connector_source_definition_id: connection.source.sourceDefinitionId,
          connector_destination_definition: connection.destination.destinationName,
          connector_destination_definition_id: connection.destination.destinationDefinitionId,
          available_streams: connection.syncCatalog.streams.length,
          enabled_streams: enabledStreams,
          type: mode,
        });
      }
    },
    [
      analyticsService,
      connection.destination.destinationDefinitionId,
      connection.destination.destinationName,
      connection.source.sourceDefinitionId,
      connection.source.sourceName,
      connection.syncCatalog.streams,
      mode,
    ]
  );

  const onScheduleChange = (item: DropDownOptionDataItem, form: FormikProps<FormikConnectionFormValues>) => {
    onDropDownSelect?.(item);

    let scheduleData: ConnectionScheduleData;
    const isManual = item.value === ConnectionScheduleType.manual;
    const isCron = item.value === ConnectionScheduleType.cron;

    // Set scheduleType for yup validation
    const scheduleType = isManual || isCron ? (item.value as ConnectionScheduleType) : ConnectionScheduleType.basic;

    // Set scheduleData.basicSchedule
    if (isManual || isCron) {
      scheduleData = {
        basicSchedule: undefined,
        cron: isCron ? CRON_DEFAULT_VALUE : undefined,
      };
    } else {
      scheduleData = {
        basicSchedule: item.value,
      };
    }

    form.setValues(
      {
        ...form.values,
        scheduleType,
        scheduleData,
      },
      true
    );
  };

  const getBasicScheduleValue = (value: ConnectionScheduleData, form: FormikProps<FormikConnectionFormValues>) => {
    const { scheduleType } = form.values;

    if (scheduleType === ConnectionScheduleType.basic) {
      return value.basicSchedule;
    }

    return formatMessage({
      id: `frequency.${scheduleType}`,
    }).toLowerCase();
  };

  const getZoneValue = (currentSelectedZone = "UTC") => currentSelectedZone;

  const onCronChange = (
    event: DropDownOptionDataItem | ChangeEvent<HTMLInputElement>,
    field: FieldInputProps<ConnectionScheduleData>,
    form: FormikProps<FormikConnectionFormValues>,
    key: string
  ) => {
    form.setFieldValue(field.name, {
      cron: {
        ...field.value?.cron,
        [key]: (event as DropDownOptionDataItem).value
          ? (event as DropDownOptionDataItem).value
          : (event as ChangeEvent<HTMLInputElement>).currentTarget.value,
      },
    });
  };

  const cronTimeZones = useMemo(() => {
    return availableCronTimeZones.map((zone: string) => ({ label: zone, value: zone }));
  }, []);

  const isCron = (form: FormikProps<FormikConnectionFormValues>): boolean => {
    return form.values.scheduleType === ConnectionScheduleType.cron;
  };

  const [, { error: cronValidationError }] = useField("scheduleData.cron.cronExpression");

  return (
    <Field name="scheduleData">
      {({ field, meta, form }: FieldProps<ConnectionScheduleData>) => (
        <>
          <FlexContainer alignItems="center">
            <div className={styles.leftFieldCol}>
              <ControlLabels
                className={styles.connectorLabel}
                nextLine
                label={formatMessage({
                  id: "form.frequency",
                })}
                infoTooltipContent={formatMessage({
                  id: "form.frequency.message",
                })}
              />
            </div>
            <div className={styles.rightFieldCol} style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
              <DropDown
                {...field}
                options={frequencies}
                data-testid="scheduleData"
                onChange={(item) => {
                  onScheduleChange(item, form);
                }}
                value={getBasicScheduleValue(field.value, form)}
              />
            </div>
          </FlexContainer>
          {isCron(form) && (
            <FlexContainer alignItems="center">
              <div className={styles.leftFieldCol}>
                <ControlLabels
                  className={styles.connectorLabel}
                  nextLine
                  error={!!meta.error && meta.touched}
                  label={formatMessage({
                    id: "form.cronExpression",
                  })}
                  infoTooltipContent={formatMessage(
                    {
                      id: "form.cronExpression.message",
                    },
                    {
                      lnk: (lnk: React.ReactNode) => (
                        <Link target="_blank" href={links.cronReferenceLink} as="a">
                          {lnk}
                        </Link>
                      ),
                    }
                  )}
                />
              </div>

              <div className={styles.rightFieldCol} style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
                <FlexContainer alignItems="center">
                  <Input
                    disabled={mode === "readonly"}
                    error={!!meta.error}
                    data-testid="cronExpression"
                    placeholder={formatMessage({
                      id: "form.cronExpression.placeholder",
                    })}
                    value={field.value?.cron?.cronExpression}
                    onChange={(event: ChangeEvent<HTMLInputElement>) =>
                      onCronChange(event, field, form, "cronExpression")
                    }
                  />
                  <DropDown
                    className={styles.cronZonesDropdown}
                    options={cronTimeZones}
                    value={getZoneValue(field.value?.cron?.cronTimeZone)}
                    onChange={(item: DropDownOptionDataItem) => onCronChange(item, field, form, "cronTimeZone")}
                  />
                </FlexContainer>
                {cronValidationError && (
                  <Text className={styles.errorMessage} data-testid="cronExpressionError">
                    <FormattedMessage id={cronValidationError} />
                  </Text>
                )}
              </div>
            </FlexContainer>
          )}
        </>
      )}
    </Field>
  );
};
