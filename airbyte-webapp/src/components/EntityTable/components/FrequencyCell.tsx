import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ConnectionScheduleData, ConnectionScheduleType } from "core/request/AirbyteClient";

interface FrequencyCellProps {
  value: ConnectionScheduleData;
  enabled?: boolean;
  scheduleType?: ConnectionScheduleType;
}

const Content = styled.div<{ enabled?: boolean }>`
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inherit")};
`;

const FrequencyCell: React.FC<FrequencyCellProps> = ({ value, enabled, scheduleType }) => {
  if (scheduleType === ConnectionScheduleType.cron || scheduleType === ConnectionScheduleType.manual) {
    return (
      <Content enabled={enabled}>
        <FormattedMessage id={`frequency.${scheduleType}`} />
      </Content>
    );
  }

  return (
    <Content enabled={enabled}>
      <FormattedMessage
        id={`frequency.${value ? value.basicSchedule?.timeUnit : "manual"}`}
        values={{ value: value.basicSchedule?.units }}
      />
    </Content>
  );
};

export default FrequencyCell;
