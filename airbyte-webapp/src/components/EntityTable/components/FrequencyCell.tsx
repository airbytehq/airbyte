import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ConnectionScheduleDataBasicSchedule } from "core/request/AirbyteClient";

interface FrequencyCellProps {
  value: ConnectionScheduleDataBasicSchedule;
  enabled?: boolean;
}

const Content = styled.div<{ enabled?: boolean }>`
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inherit")};
`;

const FrequencyCell: React.FC<FrequencyCellProps> = ({ value, enabled }) => (
  <Content enabled={enabled}>
    <FormattedMessage id={`frequency.${value ? value.timeUnit : "manual"}`} values={{ value: value?.units }} />
  </Content>
);

export default FrequencyCell;
