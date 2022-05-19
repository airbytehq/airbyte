import React from "react";
import styled from "styled-components";

import { getIcon } from "utils/imageUtils";

interface Props {
  icon?: string;
  className?: string;
  small?: boolean;
}

export const Content = styled.div<{ $small?: boolean }>`
  height: 25px;
  width: 25px;
  border-radius: ${({ $small }) => ($small ? 0 : 50)}%;
  overflow: hidden;
`;

export const ConnectorIcon: React.FC<Props> = ({ icon, className, small }) => (
  <Content className={className} $small={small} aria-hidden="true">
    {getIcon(icon)}
  </Content>
);
