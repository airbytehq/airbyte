import React from "react";
import styled from "styled-components";

import { H5, Card } from "components";

interface IProps {
  title?: string | React.ReactNode;
  className?: string;
  onClick?: () => void;
  full?: boolean;
  light?: boolean;
}

const Title = styled(H5)<{ light?: boolean; roundedBottom?: boolean }>`
  padding: ${({ light }) => (light ? "19px 20px 20px" : "25px 25px 22px")};
  color: ${({ theme }) => theme.darkPrimaryColor};
  border-bottom: ${({ light }) => (light ? "none" : "#e8e8ed 1px solid")};
  font-weight: 600;
  letter-spacing: 0.008em;
  border-radius: ${({ roundedBottom }) => (roundedBottom ? "10px 10px 0px 0px" : "10px 10px 10px 10px")};
`;

const ContentCard: React.FC<IProps> = (props) => (
  <Card className={props.className} onClick={props.onClick} full={props.full}>
    {props.title ? (
      <Title light={props.light || !props.children} roundedBottom={!!props.children}>
        {props.title}
      </Title>
    ) : null}
    {props.children}
  </Card>
);

export default ContentCard;
