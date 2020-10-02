import React from "react";
import styled from "styled-components";

// If we have errorStatus - will add it
// import StatusIcon from "../../../../../components/StatusIcon";

type IProps = {
  value: string;
  error?: boolean;
  enabled?: boolean;
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

const NameCell: React.FC<IProps> = ({ value, enabled }) => {
  return (
    <Content>
      <Space />
      {/*{enabled ? <StatusIcon success={!error} /> : <Space />}*/}
      <Name enabled={enabled}>{value}</Name>
    </Content>
  );
};

export default NameCell;
