import React from "react";
import styled from "styled-components";

interface IProps {
  height?: string;
  key?: string;
}

const MySeparator = styled.div<IProps>`
  width: 100%;
  height: ${({ height }) => (height ? height : "20px")};
`;

export const Separator: React.FC<IProps> = ({ height, key }) => {
  return <MySeparator height={height} key={key} />;
};
