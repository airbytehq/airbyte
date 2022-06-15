import React from "react";
import styled from "styled-components";

interface ConnectionCellProps {
  percent: number;
}

const Bar = styled.div`
  height: 10px;
  width: 100%;
  min-width: 150px;
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

const UsageCell: React.FC<ConnectionCellProps> = ({ percent }) => (
  <Bar>
    <Full percent={percent} />
  </Bar>
);

export default UsageCell;
