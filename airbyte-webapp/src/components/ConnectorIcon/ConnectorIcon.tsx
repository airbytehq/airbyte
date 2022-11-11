import React from "react";
import styled from "styled-components";

import { getIcon } from "utils/imageUtils";

interface Props {
  icon?: string;
  className?: string;
  small?: boolean;
}

export const Content = styled.div`
  height: 25px;
  width: 25px;
  overflow: hidden;
`;

export const ConnectorIcon: React.FC<Props> = ({ icon, className }) => (
  <Content className={className} aria-hidden="true">
    {getIcon(icon)}
  </Content>
);
