import React from "react";
import styled from "styled-components";

interface IProps {
  height?: string;
  keyProp?: string;
}

const MySeparator = styled.div<IProps>`
  width: 100%;
  height: ${({ height }) => (height ? height : "20px")};
`;

export const Separator: React.FC<IProps> = ({ height, keyProp }) => {
  return <MySeparator height={height} key={keyProp} />;
};
