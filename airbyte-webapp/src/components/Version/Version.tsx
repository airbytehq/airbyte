import React from "react";
import styled from "styled-components";

import config from "../../config";

const Content = styled.div<{ primary?: boolean }>`
  color: ${({ theme, primary }) =>
    primary ? theme.brightPrimaryColor : theme.greyColor40};
  color: ${({ theme }) => theme.greyColor40};
  letter-spacing: 0.008em;
  font-size: 12px;
  line-height: 15px;
  font-style: italic;
  margin-top: 10px;
`;

type IProps = {
  className?: string;
  primary?: boolean;
};

const Version: React.FC<IProps> = ({ className, primary }) => (
  <Content primary={primary} className={className}>
    {config.version}
  </Content>
);

export default Version;
