import React from "react";
import styled from "styled-components";

import { H5, Card } from "components";

type IProps = {
  title?: string | React.ReactNode;
  className?: string;
  onClick?: () => void;
};

const Title = styled(H5)`
  padding: 25px 25px 22px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  box-shadow: 0 1px 2px ${({ theme }) => theme.shadowColor};
  font-weight: 600;
  letter-spacing: 0.008em;
  border-radius: 10px 10px 0 0;
`;

const ContentCard: React.FC<IProps> = (props) => (
  <Card className={props.className} onClick={props.onClick}>
    {props.title ? <Title>{props.title}</Title> : null}
    {props.children}
  </Card>
);

export default ContentCard;
