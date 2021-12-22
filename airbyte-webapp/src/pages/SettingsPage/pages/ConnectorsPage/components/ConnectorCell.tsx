import React from "react";
import styled from "styled-components";

import Indicator from "components/Indicator";
import { getIcon } from "utils/imageUtils";
import { FormattedMessage } from "react-intl";

type IProps = {
  connectorName: string;
  img?: string;
  hasUpdate?: boolean;
  isDeprecated?: boolean;
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

const CustomAnnotation = styled.span`
  color: ${({ theme }) => theme.greyColor40};
`;

const ConnectorCell: React.FC<IProps> = ({
  connectorName,
  img,
  hasUpdate,
  isDeprecated,
}) => {
  return (
    <Content>
      {hasUpdate && <Notification />}
      <Image>{getIcon(img)}</Image>
      <span>
        {connectorName}{" "}
        {isDeprecated ? (
          <CustomAnnotation>
            ( <FormattedMessage id="admin.customImage" /> )
          </CustomAnnotation>
        ) : null}
      </span>
    </Content>
  );
};

export default ConnectorCell;
