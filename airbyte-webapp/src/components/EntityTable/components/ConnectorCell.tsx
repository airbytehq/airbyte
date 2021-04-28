import React from "react";
import styled from "styled-components";

import ImageBlock from "components/ImageBlock";
import { getIcon } from "../../../utils/imageUtils";

type IProps = {
  value: string;
  enabled?: boolean;
  img?: React.ReactNode | string;
};

const Content = styled.div<{ enabled?: boolean }>`
  display: flex;
  align-items: center;
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inheret")};
  font-weight: 500;
`;

const Image = styled(ImageBlock)`
  margin-right: 6px;
`;

const ConnectorCell: React.FC<IProps> = ({ value, enabled, img }) => {
  return (
    <Content enabled={enabled}>
      <Image small img={getIcon({ icon: img })} />
      {value}
    </Content>
  );
};

export default ConnectorCell;
