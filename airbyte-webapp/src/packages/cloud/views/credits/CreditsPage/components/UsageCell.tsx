import React from "react";
import styled from "styled-components";

type ConnectionCellProps = {
  value: number;
  percent: number;
};

const Content = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Value = styled.div`
  padding-right: 10px;
  font-weight: 500;
  font-size: 14px;
  line-height: 17px;
  flex: 1 0 0;
  min-width: 50px;
`;

const Bar = styled.div`
  height: 10px;
  width: 100%;
  background: ${({ theme }) => theme.greyColor20};
  flex: 10 0 0;
  overflow: hidden;
  border-radius: 0 4px 4px 0;
`;

const Full = styled.div<{ percent: number }>`
  height: 100%;
  width: ${({ percent }) => percent}%;
  background: ${({ theme }) => theme.lightTextColor};
  opacity: 0.5;
`;

const UsageCell: React.FC<ConnectionCellProps> = ({ value, percent }) => {
  return (
    <Content>
      <Value>{value}</Value>
      <Bar>
        <Full percent={percent} />
      </Bar>
    </Content>
  );
};

export default UsageCell;
