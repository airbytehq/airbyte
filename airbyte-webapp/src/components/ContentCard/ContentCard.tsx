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

const Title = styled(H5)<{ $light?: boolean }>`
  padding: ${({ $light }) => ($light ? "19px 20px 20px" : "25px 25px 22px")};
  color: ${({ theme }) => theme.darkPrimaryColor};
  box-shadow: ${({ $light, theme }) =>
    $light ? "none" : `0 1px 2px ${theme.shadowColor}`};
  font-weight: 600;
  letter-spacing: 0.008em;
  border-radius: 10px 10px 0 0;
`;

const ContentCard: React.FC<IProps> = (props) => (
  <Card className={props.className} onClick={props.onClick} full={props.full}>
    {props.title ? <Title $light={props.$light}>{props.title}</Title> : null}
    {props.children}
  </Card>
);

export default ContentCard;
