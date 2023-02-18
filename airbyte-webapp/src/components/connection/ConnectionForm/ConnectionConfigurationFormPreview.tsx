import { useFormikContext } from "formik";
import { FormattedMessage } from "react-intl";

import { FlexContainer } from "components/ui/Flex";
import { Text } from "components/ui/Text";

import {
  ConnectionScheduleData,
  ConnectionScheduleType,
  NonBreakingChangesPreference,
} from "core/request/AirbyteClient";
import { FeatureItem, useFeature } from "hooks/services/Feature";

import styles from "./ConnectionConfigurationFormPreview.module.scss";

export const ConnectionConfigurationFormPreview: React.FC = () => {
  const { getFieldMeta } = useFormikContext();
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);

  const scheduleType = getFieldMeta<ConnectionScheduleType>("scheduleType").value;
  const scheduleData = getFieldMeta<ConnectionScheduleData>("scheduleData").value;
  const nonBreakingChangesPreference = getFieldMeta<NonBreakingChangesPreference>("nonBreakingChangesPreference").value;

  const frequency = (
    <div>
      <Text size="xs" color="grey">
        <FormattedMessage id="form.frequency" />:
      </Text>
      <Text size="md" color="grey">
        {scheduleType === ConnectionScheduleType.manual && <FormattedMessage id="frequency.manual" />}
        {scheduleType === ConnectionScheduleType.cron && (
          <>
            <FormattedMessage id="frequency.cron" /> - {scheduleData?.cron?.cronExpression}{" "}
            {scheduleData?.cron?.cronTimeZone}
          </>
        )}
        {scheduleType === ConnectionScheduleType.basic && (
          <FormattedMessage
            id={`form.every.${scheduleData?.basicSchedule?.timeUnit}`}
            values={{ value: scheduleData?.basicSchedule?.units }}
          />
        )}
      </Text>
    </div>
  );

  const nonBreakingChanges = allowAutoDetectSchema && (
    <div>
      <Text size="xs" color="grey">
        <FormattedMessage id="connectionForm.nonBreakingChangesPreference.label" />:
      </Text>
      <Text size="md" color="grey">
        <FormattedMessage id={`connectionForm.nonBreakingChangesPreference.${nonBreakingChangesPreference}`} />
      </Text>
    </div>
  );

  return (
    <FlexContainer className={styles.container}>
      {frequency}
      {nonBreakingChanges}
    </FlexContainer>
  );
};
