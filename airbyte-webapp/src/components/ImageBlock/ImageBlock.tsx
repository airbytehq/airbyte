import React from "react";
import styled from "styled-components";

import { getIcon } from "utils/imageUtils";

type IProps = {
  img?: string;
  className?: string;
  num?: number;
  small?: boolean;
};

export const Content = styled.div<{ small?: boolean }>`
  height: 25px;
  width: 25px;
  min-width: 25px;
  background: ${({ theme, small }) => (small ? "none" : theme.brightColor)};
  box-shadow: ${({ theme, small }) => (small ? "none" : `0 1px 2px 0 ${theme.shadowColor}`)};
  border-radius: ${({ small }) => (small ? 0 : 50)}%;
  text-align: center;

  overflow: hidden;
`;

export const Number = styled.div`
  font-weight: 500;
  font-size: 14px;
  color: ${({ theme }) => theme.primaryColor};
  padding: 4px 0 3px;
`;

const ImageBlock: React.FC<IProps> = ({ img, className, num, small }) => (
  <Content className={className} small={small && !num}>
    {num ? <Number>{num}</Number> : <>{getIcon(img)}</>}
  </Content>
);

export default ImageBlock;
export { ImageBlock };
