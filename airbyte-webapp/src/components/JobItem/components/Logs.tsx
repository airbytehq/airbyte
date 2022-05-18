import React from "react";
import { FormattedMessage } from "react-intl";
import { LazyLog } from "react-lazylog";
import styled from "styled-components";

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
  logTimestamp?: number;
};

const Logs: React.FC<LogsProps> = ({ logsArray, logTimestamp }) => {
  const logsJoin = logsArray?.length ? logsArray.join("\n") : "No logs available";
  const matchingLineNumbers = getMatchingLineNumbers(logTimestamp, logsArray);

  return (
    <LogsView isEmpty={!logsArray}>
      {logsArray ? (
        <LazyLog
          text={logsJoin}
          lineClassName="logLine"
          highlightLineClassName="highlightLogLine"
          selectableLines
          follow={matchingLineNumbers.length > 0 ? false : true}
          style={{ background: "transparent" }}
          scrollToLine={matchingLineNumbers.length > 0 ? matchingLineNumbers[0] - 1 : undefined}
          highlight={matchingLineNumbers}
        />
      ) : (
        <FormattedMessage id="sources.emptyLogs" />
      )}
    </LogsView>
  );
};

/**
 * Matching the log's line number by time makes the following assumptions:
 * 1. The log's lines are already ordered by time
 * 2. The timestamps used are in the same timezone
 */
const getMatchingLineNumbers = (matchTimestamp: number | undefined, lines: string[] | undefined) => {
  const matchingLineNumbers: number[] = [];
  if (!matchTimestamp || !lines) {
    return matchingLineNumbers;
  }

  let lineCounter = 0;
  if (matchTimestamp && lines && lines.length > 0) {
    for (const line of lines) {
      // matches the the start of a line like "2022-05-17 23:00:19 DEBUG I am a log message"
      const timeString = line.match(
        /^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9]/
      );
      if (timeString) {
        const datetime = Date.parse(`${timeString[0].replace(" ", "T")}Z`);
        if (datetime - 1000 <= matchTimestamp && datetime + 1000 >= matchTimestamp) {
          // TODO: it appears that LazyLog only highlights the first 2 lines in the array
          matchingLineNumbers.push(lineCounter + 1);
        }
      }
      lineCounter++;
    }
  }

  return matchingLineNumbers;
};

export default Logs;
