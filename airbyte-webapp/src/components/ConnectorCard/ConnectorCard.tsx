import styled from "styled-components";

import { ReleaseStageBadge } from "components/ReleaseStageBadge";

import { ReleaseStage } from "core/request/AirbyteClient";
import { getIcon } from "utils/imageUtils";

interface Props {
  connectionName: string;
  icon?: string;
  connectorName: string;
  releaseStage?: ReleaseStage;
}

const MainComponent = styled.div`
  display: flex;
  padding: 10px;
  width: 220px;
  align-items: center;
`;

const Details = styled.div`
  width: 160px;
  margin-left: 10px;
  display: flex;
  flex-direction: column;
  font-weight: normal;
`;

const EntityIcon = styled.div`
  height: 30px;
  width: 30px;
`;

const ConnectionName = styled.div`
  font-size: 14px;
  color: #1a194d;
  text-align: left;
  margin-right: 10px;
`;

const ConnectorDetails = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: center;
`;

const ConnectorName = styled.div`
  font-size: 11px;
  margin-top: 1px;
  color: #afafc1;
  text-align: left;
  word-wrap: break-word;
`;

const ConnectorCard = (props: Props) => {
  const { connectionName, connectorName, icon, releaseStage } = props;

  return (
    <MainComponent>
      {icon && <EntityIcon>{getIcon(icon)}</EntityIcon>}
      <Details>
        <ConnectorDetails>
          <ConnectionName>{connectionName}</ConnectionName>
          {releaseStage && <ReleaseStageBadge stage={releaseStage} />}
        </ConnectorDetails>
        <ConnectorName>{connectorName} </ConnectorName>
      </Details>
    </MainComponent>
  );
};

export default ConnectorCard;
