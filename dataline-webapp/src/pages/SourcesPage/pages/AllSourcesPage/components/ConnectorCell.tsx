import React from "react";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import ImageBlock from "../../../../../components/ImageBlock";
import SourceResource from "../../../../../core/resources/Source";

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
  const source = useResource(SourceResource.detailShape(), {
    sourceId: value
  });

  return (
    <Content enabled={enabled}>
      <Image />
      {source.name}
    </Content>
  );
};

export default StatusCell;
