import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCalendarAlt } from "@fortawesome/free-regular-svg-icons";
import { FormattedRelativeTime } from "react-intl";

const CalendarIcon = styled(FontAwesomeIcon)`
  color: ${({ theme }) => theme.greyColor40};
  font-size: 14px;
  line-height: 14px;
  margin-right: 5px;
`;

const Content = styled.div<{ enabled?: boolean }>`
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inheret")};
`;

type IProps = {
  value: number;
  enabled?: boolean;
};

const LastSyncCell: React.FC<IProps> = ({ value, enabled }) => (
  <Content enabled={enabled}>
    <CalendarIcon icon={faCalendarAlt} />
    <FormattedRelativeTime
      value={(value - Date.now()) / 1000}
      updateIntervalInSeconds={60}
    />
  </Content>
);

export default LastSyncCell;
