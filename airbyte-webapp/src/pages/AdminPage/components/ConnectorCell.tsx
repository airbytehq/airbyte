import React from "react";
import styled from "styled-components";

type IProps = {
  connectorName: string;
  img?: string;
};

const Content = styled.div<{ enabled?: boolean }>`
  display: flex;
  align-items: center;
  padding-left: 30px;
`;

const Image = styled.img`
  height: 17px;
  margin-right: 9px;
`;

const ConnectorCell: React.FC<IProps> = ({ connectorName, img }) => {
  return (
    <Content>
      <Image src={img || "/default-logo-catalog.svg"} alt={"logo"} />
      {connectorName}
    </Content>
  );
};

export default ConnectorCell;
