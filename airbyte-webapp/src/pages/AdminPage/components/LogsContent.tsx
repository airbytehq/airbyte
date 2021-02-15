import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useFetcher } from "rest-hooks";

import Button from "../../../components/Button";
import LogsResource from "../../../core/resources/Logs";

const Content = styled.div`
  padding: 29px 0 27px;
  text-align: center;
`;

const LogsButton = styled(Button)`
  margin: 0 15px;
`;

const LogsContent: React.FC = () => {
  const fetchLogs = useFetcher(LogsResource.detailShape());

  const downloadLogs = async (logType: string) => {
    const { file } = await fetchLogs({ logType });

    const element = document.createElement("a");
    element.href = URL.createObjectURL(file);
    element.download = `${logType}-logs.txt`;
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
    document.body.removeChild(element);
  };

  return (
    <Content>
      <LogsButton onClick={() => downloadLogs("server")}>
        <FormattedMessage id="admin.downloadServerLogs" />
      </LogsButton>
      <LogsButton onClick={() => downloadLogs("scheduler")}>
        <FormattedMessage id="admin.downloadSchedulerLogs" />
      </LogsButton>
    </Content>
  );
};

export default LogsContent;
