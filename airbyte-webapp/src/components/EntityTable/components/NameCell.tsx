import React from "react";
import styled from "styled-components";
import { useIntl } from "react-intl";

import StatusIcon from "components/StatusIcon";
import ImageBlock from "components/ImageBlock";
import { Status } from "../types";

type IProps = {
  value: string;
  enabled?: boolean;
  status?: string | null;
  icon?: boolean;
  img?: string;
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

const NameCell: React.FC<IProps> = ({ value, enabled, status, icon, img }) => {
  const formatMessage = useIntl().formatMessage;
  const title =
    status === Status.EMPTY
      ? formatMessage({
          id: "connection.noSyncData",
        })
      : status === Status.INACTIVE
      ? formatMessage({
          id: "connection.disabledConnection",
        })
      : status === Status.ACTIVE
      ? formatMessage({
          id: "connection.successSync",
        })
      : formatMessage({
          id: "connection.failedSync",
        });

  return (
    <Content>
      {status ? (
        <StatusIcon
          title={title}
          empty={status === Status.EMPTY}
          success={status === Status.ACTIVE}
          inactive={status === Status.INACTIVE}
        />
      ) : (
        <Space />
      )}
      {icon && <Image small img={img} />}
      <Name enabled={enabled}>{value}</Name>
    </Content>
  );
};

export default NameCell;
