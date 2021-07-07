import styled from "styled-components";
import React from "react";
import { FormattedMessage } from "react-intl";
import { LazyLog } from "react-lazylog";

const LogsView = styled.div<{ isEmpty?: boolean }>`
  padding: 11px ${({ isEmpty }) => (isEmpty ? 42 : 12)}px 20px;
  font-size: 12px;
  line-height: 18px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  font-family: ${({ theme }) => theme.codeFont};
  word-wrap: break-word;
  min-height: ${({ isEmpty }) => (isEmpty ? "auto" : "400px")};

  & .logLine {
    font-size: 10px;
    color: ${({ theme }) => theme.darkPrimaryColor};

    &.highlightLogLine {
      background: ${({ theme }) => theme.greyColor40};
    }

    &:hover {
      background: ${({ theme }) => theme.greyColor30};
    }

    & > a {
      margin-left: 5px;
      margin-right: 10px;
      width: 45px;
    }
  }
`;

type LogsProps = {
  logsArray?: string[];
};

const Logs: React.FC<LogsProps> = ({ logsArray }) => {
  const logsJoin = logsArray && logsArray.length ? logsArray.join("\n") : "";

  return (
    <LogsView isEmpty={!logsArray}>
      {logsArray ? (
        <LazyLog
          text={logsJoin}
          lineClassName="logLine"
          highlightLineClassName="highlightLogLine"
          selectableLines
          follow
          style={{ background: "transparent" }}
        />
      ) : (
        <FormattedMessage id="sources.emptyLogs" />
      )}
    </LogsView>
  );
};

export default Logs;
