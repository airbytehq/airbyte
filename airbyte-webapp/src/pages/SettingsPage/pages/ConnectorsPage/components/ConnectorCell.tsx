import React from "react";
import styled from "styled-components";

import Indicator from "components/Indicator";
import { getIcon } from "utils/imageUtils";

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
  margin: -5px 0;
  min-width: 290px;
`;

const Image = styled.div`
  height: 25px;
  width: 17px;
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
      <Image>{getIcon(img)}</Image>
      {connectorName}
    </Content>
  );
};

export default ConnectorCell;
