import React from "react";
import styled from "styled-components";
import Indicator from "../../../components/Indicator";

type IProps = {
  connectorName: string;
  img?: string;
  hasUpdate?: boolean;
};

const Content = styled.div<{ enabled?: boolean }>`
  display: flex;
  align-items: center;
  padding-left: 30px;
  position: relative;
`;

const Image = styled.img`
  height: 17px;
  margin-right: 9px;
`;

const Notification = styled(Indicator)`
  position: absolute;
  left: 8px;
`;

const ConnectorCell: React.FC<IProps> = ({ connectorName, img, hasUpdate }) => {
  return (
    <Content>
      {hasUpdate && <Notification />}
      <Image src={img || "/default-logo-catalog.svg"} alt={"logo"} />
      {connectorName}
    </Content>
  );
};

export default ConnectorCell;
