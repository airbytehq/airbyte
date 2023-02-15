import classNames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";

import { Text } from "components/ui/Text";

import { ConnectionScheduleData, ConnectionScheduleType } from "core/request/AirbyteClient";

import styles from "./FrequencyCell.module.scss";

interface FrequencyCellProps {
  value?: ConnectionScheduleData;
  enabled?: boolean;
  scheduleType?: ConnectionScheduleType;
}

export const FrequencyCell: React.FC<FrequencyCellProps> = ({ value, enabled, scheduleType }) => {
  if (scheduleType === ConnectionScheduleType.cron || scheduleType === ConnectionScheduleType.manual) {
    return (
      <Text className={classNames(styles.text, { [styles.enabled]: enabled })} size="sm">
        <FormattedMessage id={`frequency.${scheduleType}`} />
      </Text>
    );
  }

  return (
    <Text className={classNames(styles.text, { [styles.enabled]: enabled })} size="sm">
      <FormattedMessage
        id={`frequency.${value?.basicSchedule?.timeUnit ?? "manual"}`}
        values={{ value: value?.basicSchedule?.units }}
      />
    </Text>
  );
};
