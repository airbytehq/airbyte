import { FormattedMessage } from "react-intl";
import { LazyLog } from "react-lazylog";
import styled from "styled-components";

const LogsView = styled.div<{ isEmpty?: boolean }>`
  padding: 11px ${({ isEmpty }) => (isEmpty ? 42 : 12)}px 20px;
  font-size: 12px;
  line-height: 18px;
  color: ${({ theme }) => theme.darkPrimaryColor};
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

interface LogsProps {
  logsArray?: string[];
}

const Logs: React.FC<LogsProps> = ({ logsArray }) => {
  const logsJoin = logsArray?.length ? logsArray.join("\n") : "No logs available";

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
          scrollToLine={undefined}
          highlight={[]}
        />
      ) : (
        <FormattedMessage id="sources.emptyLogs" />
      )}
    </LogsView>
  );
};

export default Logs;
