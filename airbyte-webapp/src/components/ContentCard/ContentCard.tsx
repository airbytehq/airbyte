import React from "react";
import styled from "styled-components";

import { H5 } from "components/Titles";

type IProps = {
  title?: string | React.ReactNode;
  description?: string | React.ReactNode;
  attentionMessage?: string | React.ReactNode;
  className?: string;
  onClick?: () => void;
};

const Card = styled.div`
  background: ${({ theme }) => theme.whiteColor};
  border-radius: 8px;
  box-shadow: 0 1px 2px ${({ theme }) => theme.shadowColor};
  border: 1px solid ${({ theme }) => theme.greyColor20};
`;

const Title = styled(H5)`
  padding: 25px 25px 22px;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  color: ${({ theme }) => theme.darkPrimaryColor};
  box-shadow: 0 1px 2px ${({ theme }) => theme.shadowColor};
  font-weight: 600;
  letter-spacing: 0.008em;
`;

const Attention = styled.span`
  font-weight: normal;
  color: ${({ theme }) => theme.dangerColor};
`;

const Description = styled.div`
  font-weight: normal;
  color: ${({ theme }) => theme.greyColor40};
  font-size: 15px;
  line-height: 18px;
  margin: 5px 0 -10px;
`;

const ContentCard: React.FC<IProps> = (props) => (
  <Card className={props.className} onClick={props.onClick}>
    {props.title ? (
      <Title>
        {props.title}
        {props.attentionMessage && (
          <>
            {" "}
            - <Attention>{props.attentionMessage}</Attention>
          </>
        )}
        {props.description && <Description>{props.description}</Description>}
      </Title>
    ) : null}
    {props.children}
  </Card>
);

export default ContentCard;
