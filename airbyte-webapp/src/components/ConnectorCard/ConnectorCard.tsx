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
  // width: 220px;
  width: 100%;
  align-items: center;
`;

const Details = styled.div`
  // width: 160px;
  //  width: 100%;
  flex: 1;
  margin-left: 22px;
  display: flex;
  flex-direction: column;
  font-weight: normal;
`;

const EntityIcon = styled.div`
  width: 126px;
  height: 126px;
  box-shadow: 0px 10px 12px rgba(74, 74, 87, 0.1);
  border-radius: 18px;
  padding: 6px;
  box-sizing: border-box;
`;

const ConnectionName = styled.div`
  font-size: 24px;
  text-align: left;
  margin-right: 10px;
  font-weight: 500;
  line-height: 30px;
  color: #27272a;
  flex: 1;
`;

const ConnectorDetails = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: center;
`;

// const ConnectorName = styled.div`
//   font-size: 11px;
//   margin-top: 1px;
//   color: #afafc1;
//   text-align: left;
//   word-wrap: break-word;
// `;

const ConnectorCard = (props: Props) => {
  const { connectionName, icon, releaseStage } = props; // connectorName

  return (
    <MainComponent>
      {icon && <EntityIcon>{getIcon(icon)}</EntityIcon>}
      <Details>
        <ConnectorDetails>
          <ConnectionName>{connectionName}</ConnectionName>
          {releaseStage && <ReleaseStageBadge stage={releaseStage} />}
        </ConnectorDetails>
        {/* <ConnectorName>{connectorName} </ConnectorName> */}
      </Details>
    </MainComponent>
  );
};

export default ConnectorCard;
