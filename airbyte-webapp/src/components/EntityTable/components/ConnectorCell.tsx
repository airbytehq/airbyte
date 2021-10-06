import React from "react";
import styled from "styled-components";

import ImageBlock from "components/ImageBlock";

type IProps = {
  value: string;
  enabled?: boolean;
  img?: string;
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
      <Image small img={img} />
      {value}
    </Content>
  );
};

export default ConnectorCell;
