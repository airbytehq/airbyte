import React from "react";
// import { useIntl } from "react-intl";
import styled from "styled-components";

// import { ConnectorIcon } from "components/ConnectorIcon";
// import StatusIcon from "components/StatusIcon";
// import { StatusIconStatus } from "components/StatusIcon/StatusIcon";

// import { Status } from "../types";

interface Props {
  value: string;
  enabled?: boolean;
  status?: string | null;
  icon?: boolean;
  img?: string;
  onClickRow?: () => void;
}

const Content = styled.div`
  display: flex;
  align-items: center;
  font-weight: 500;
`;

const Name = styled.div<{ enabled?: boolean }>`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 280px;
  // color: ${({ theme, enabled }) => (!enabled ? theme.greyColor40 : "inherit")};
  color: inherit;
  &:hover {
    color: ${({ theme }) => theme.primaryColor};
    cursor: pointer;
  }
`;

// const Image = styled(ConnectorIcon)`
//   margin-right: 6px;
// `;

const NameCell: React.FC<Props> = ({
  value,
  enabled, // status, icon, img
  onClickRow,
}) => {
  // const { formatMessage } = useIntl();
  // const statusIconStatus = useMemo<StatusIconStatus | undefined>(
  //   () =>
  //     status === Status.EMPTY
  //       ? "sleep"
  //       : status === Status.ACTIVE
  //       ? "success"
  //       : status === Status.INACTIVE
  //       ? "inactive"
  //       : status === Status.PENDING
  //       ? "loading"
  //       : undefined,
  //   [status]
  // );
  // const title =
  //   status === Status.EMPTY
  //     ? formatMessage({
  //         id: "connection.noSyncData",
  //       })
  //     : status === Status.INACTIVE
  //     ? formatMessage({
  //         id: "connection.disabledConnection",
  //       })
  //     : status === Status.ACTIVE
  //     ? formatMessage({
  //         id: "connection.successSync",
  //       })
  //     : status === Status.PENDING
  //     ? formatMessage({
  //         id: "connection.pendingSync",
  //       })
  //     : formatMessage({
  //         id: "connection.failedSync",
  //       });

  return (
    <Content onClick={() => onClickRow?.()}>
      {/* {status && <StatusIcon title={title} status={statusIconStatus} />}
      {icon && <Image icon={img} />} */}
      <Name enabled={enabled}>{value}</Name>
    </Content>
  );
};

export default NameCell;
