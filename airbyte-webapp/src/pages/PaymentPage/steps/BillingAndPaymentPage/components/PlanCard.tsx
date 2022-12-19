import React from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";

import { Separator } from "components/Separator";

const Container = styled.div`
  min-width: 400px;
  display: flex;
  flex-direction: column;
`;

const PlanCardContainer = styled.div`
  width: 100%;
  background-color: ${({ theme }) => theme.white};
  padding: 60px 30px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const Logo = styled.img`
  width: 50px;
  height: 35px;
`;

const HeadingText = styled.div`
  font-weight: 500;
  font-size: 22px;
  line-height: 30px;
  display: flex;
  align-items: center;
  color: ${({ theme }) => theme.black300};
`;

const PlanRow = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const PlanHeadline = styled.div`
  min-width: 140px;
  font-weight: 500;
  font-size: 13px;
  line-height: 20px;
  color: ${({ theme }) => theme.black300};
`;

const PlanText = styled.div`
  font-weight: 400;
  font-size: 13px;
  line-height: 20px;
  color: ${({ theme }) => theme.black300};
`;

const LinksContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-around;
`;

const FooterLink = styled(Link)`
  font-weight: 400;
  font-size: 12px;
  line-height: 20px;
  color: #6b6b6f;
`;

const PlanCard: React.FC = () => {
  return (
    <Container>
      <PlanCardContainer>
        <Logo src="/daspireLogo.svg" alt="logo" />
        <Separator />
        <HeadingText>Professional Plan</HeadingText>
        <Separator height="65px" />
        <PlanRow>
          <PlanHeadline>No. of rows</PlanHeadline>
          <PlanText>2 million</PlanText>
        </PlanRow>
        <Separator height="45px" />
        <PlanRow>
          <PlanHeadline>Monthly billing</PlanHeadline>
          <PlanText>US$58 / month</PlanText>
        </PlanRow>
        <Separator height="45px" />
        <PlanRow>
          <PlanHeadline>Total due today</PlanHeadline>
          <PlanText>US$58</PlanText>
        </PlanRow>
        <Separator height="45px" />
        <PlanRow>
          <PlanHeadline>
            Reoccuring
            <br />
            billing
          </PlanHeadline>
          <PlanText>Next billing date: 20 Nov 2022 You can cancel at any time.</PlanText>
        </PlanRow>
      </PlanCardContainer>
      <Separator height="45px" />
      <LinksContainer>
        <FooterLink to="#">Terms of Service</FooterLink>
        <FooterLink to="#">Privacy Policy</FooterLink>
      </LinksContainer>
    </Container>
  );
};

export default PlanCard;
