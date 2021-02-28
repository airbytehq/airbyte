import React from "react";
import styled from "styled-components";

import { H5 } from "components/Titles";

type IProps = {
  title: string | React.ReactNode;
  text: string | React.ReactNode;
};

const Singleton = styled.div`
  position: fixed;
  bottom: 0px;
  left: 50%;
  transform: translate(-50%, -50%);

  padding: 25px 25px 22px;

  background: ${({ theme }) => theme.lightPrimaryColor};
  border: 1px solid ${({ theme }) => theme.greyColor20};
  box-shadow: 0px 1px 2px ${({ theme }) => theme.shadowColor};
  border-radius: 8px;
`;

const Title = styled(H5)`
  margin-bottom: 5px;

  color: ${({ theme }) => theme.primaryColor};

  font-style: normal;
  font-weight: bold;
  font-size: 15px;
  line-height: 18px;
`;

const Text = styled.div`
  color: ${({ theme }) => theme.mediumPrimaryColor};

  font-style: normal;
  font-weight: normal;
  font-size: 14px;
  line-height: 17px;
`;

const SingletonCard: React.FC<IProps> = (props) => (
  <Singleton>
    <Title>{props.title}</Title>
    <Text>{props.text}</Text>
  </Singleton>
);

export default SingletonCard;
