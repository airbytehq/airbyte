import React from "react";
import styled from "styled-components";

import ImageBlock from "../../../../../components/ImageBlock";

type IProps = {
  value: string;
  enabled?: boolean;
};

const Content = styled.div<{ enabled?: boolean }>`
  display: flex;
  align-items: center;
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inheret")};
`;

const Image = styled(ImageBlock)`
  margin-right: 6px;
`;

const StatusCell: React.FC<IProps> = ({ value, enabled }) => {
  return (
    <Content enabled={enabled}>
      <Image />
      {value}
    </Content>
  );
};

export default StatusCell;
