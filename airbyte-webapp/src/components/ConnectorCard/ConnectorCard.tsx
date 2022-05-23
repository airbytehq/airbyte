import styled from "styled-components";

import { ReleaseStageBadge } from "components/ReleaseStageBadge";

import { ReleaseStage } from "core/request/AirbyteClient";
import { getIcon } from "utils/imageUtils";

type Props = {
  connectionName: string;
  icon?: string;
  connectorName: string;
  releaseStage?: ReleaseStage;
};

const MainComponent = styled.div`
  display: flex;
  padding: 10px;
`;

const Details = styled.div`
  margin-left: 10px;
  display: flex;
  flex-direction: column;
  font-weight: normal;
`;

const EntityIcon = styled.div`
  height: 40px;
  width: 40px;
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
  color: #afafc1;
  text-align: left;
`;

function ConnectorCard(props: Props) {
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
}

export default ConnectorCard;
