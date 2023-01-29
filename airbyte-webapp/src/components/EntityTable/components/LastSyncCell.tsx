import React from "react";
import { FormattedRelativeTime } from "react-intl";
import styled from "styled-components";

const Content = styled.div<{ enabled?: boolean }>`
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inherit")};
`;

interface Props {
  timeInSeconds?: number | null;
  enabled?: boolean;
}

const LastSyncCell: React.FC<Props> = ({ timeInSeconds, enabled }) => {
  if (!timeInSeconds) {
    return null;
  }

  return (
    <Content enabled={enabled}>
      <FormattedRelativeTime value={timeInSeconds - Date.now() / 1000} updateIntervalInSeconds={60} />
    </Content>
  );
};

export default LastSyncCell;
