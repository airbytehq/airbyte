import React from "react";
import styled from "styled-components";

import StatusIcon from "components/StatusIcon";
import ImageBlock from "components/ImageBlock";
import { Status } from "../types";

type IProps = {
  value: string;
  enabled?: boolean;
  status?: string | null;
  icon?: boolean;
};

const Content = styled.div`
  display: flex;
  align-items: center;
  font-weight: 500;
`;

const Name = styled.div<{ enabled?: boolean }>`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 500px;
  color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inherit")};
`;

const Space = styled.div`
  width: 30px;
  height: 20px;
  opacity: 0;
`;

const Image = styled(ImageBlock)`
  margin-right: 6px;
`;

const NameCell: React.FC<IProps> = ({ value, enabled, status, icon }) => {
  return (
    <Content>
      {status ? (
        <StatusIcon
          empty={status === Status.EMPTY}
          success={status === Status.ACTIVE}
          inactive={status === Status.INACTIVE}
        />
      ) : (
        <Space />
      )}
      {icon && <Image small />}
      <Name enabled={enabled}>{value}</Name>
    </Content>
  );
};

export default NameCell;
