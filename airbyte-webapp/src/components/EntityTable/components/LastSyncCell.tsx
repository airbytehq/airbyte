import { faCalendarAlt } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedRelativeTime } from "react-intl";
import styled from "styled-components";

const CalendarIcon = styled(FontAwesomeIcon)`
  color: ${({ theme }) => theme.greyColor40};
  font-size: 14px;
  line-height: 14px;
  margin-right: 5px;
`;

const Content = styled.div<{ enabled?: boolean }>`
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inheret")};
`;

interface IProps {
  timeInSecond: number;
  enabled?: boolean;
}

const LastSyncCell: React.FC<IProps> = ({ timeInSecond, enabled }) => {
  if (!timeInSecond) {
    return null;
  }

  return (
    <Content enabled={enabled}>
      <CalendarIcon icon={faCalendarAlt} />
      <FormattedRelativeTime value={timeInSecond - Date.now() / 1000} updateIntervalInSeconds={60} />
    </Content>
  );
};

export default LastSyncCell;
