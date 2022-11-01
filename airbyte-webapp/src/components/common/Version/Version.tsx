import React from "react";
import styled from "styled-components";

import { useConfig } from "config";

const Content = styled.div<{ primary?: boolean }>`
  color: ${({ theme, primary }) => (primary ? theme.brightPrimaryColor : theme.greyColor40)};
  color: ${({ theme }) => theme.greyColor40};
  letter-spacing: 0.008em;
  font-size: 12px;
  line-height: 15px;
  font-style: italic;
  margin-top: 10px;
`;

interface VersionProps {
  className?: string;
  primary?: boolean;
}

export const Version: React.FC<VersionProps> = ({ className, primary }) => {
  const config = useConfig();
  return (
    <Content primary={primary} className={className}>
      {config.version}
    </Content>
  );
};
