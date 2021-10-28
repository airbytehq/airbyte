import React from "react";
import styled from "styled-components";

import { H5, Card } from "components";

type IProps = {
  title?: string | React.ReactNode;
  className?: string;
  onClick?: () => void;
  full?: boolean;
  $light?: boolean;
};

const Title = styled(H5)`
  font-weight: 600;
  letter-spacing: 0.008em;
`;

const Header = styled.div<{ $light?: boolean }>`
  padding: ${({ $light }) => ($light ? "19px 20px 20px" : "25px 25px 22px")};
  color: ${({ theme }) => theme.darkPrimaryColor};
  box-shadow: ${({ $light, theme }) =>
    $light ? "none" : `0 1px 2px ${theme.shadowColor}`};
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 10px 10px 0 0;
  height: 80px;
`;

const ContentCard: React.FC<IProps> = (props) => (
  <Card className={props.className} onClick={props.onClick} full={props.full}>
    <Header $light={props.$light}>
      {props.title ? <Title>{props.title}</Title> : null}
    </Header>
    {props.children}
  </Card>
);

export default ContentCard;
