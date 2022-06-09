import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import Indicator from "components/Indicator";
import { ReleaseStageBadge } from "components/ReleaseStageBadge";

import { ReleaseStage } from "core/request/AirbyteClient";
import { getIcon } from "utils/imageUtils";

interface ConnectorCellProps {
  connectorName: string;
  img?: string;
  hasUpdate?: boolean;
  isDeprecated?: boolean;
  releaseStage?: ReleaseStage;
}

const Content = styled.div<{ enabled?: boolean }>`
  display: flex;
  align-items: center;
  padding-left: 30px;
  position: relative;
  margin: -5px 0;
  min-width: 290px;
  gap: 8px;
`;

const Image = styled.div`
  height: 25px;
  width: 17px;
`;

const Notification = styled(Indicator)`
  position: absolute;
  left: 8px;
`;

const CustomAnnotation = styled.span`
  color: ${({ theme }) => theme.greyColor40};
`;

const ConnectorCell: React.FC<ConnectorCellProps> = ({ connectorName, img, hasUpdate, isDeprecated, releaseStage }) => {
  return (
    <Content>
      {hasUpdate && <Notification />}
      <Image>{getIcon(img)}</Image>
      <span>{connectorName}</span>
      <ReleaseStageBadge small tooltip={false} stage={releaseStage} />
      {isDeprecated && (
        <CustomAnnotation>
          (<FormattedMessage id="admin.customImage" />)
        </CustomAnnotation>
      )}
    </Content>
  );
};

export default ConnectorCell;
