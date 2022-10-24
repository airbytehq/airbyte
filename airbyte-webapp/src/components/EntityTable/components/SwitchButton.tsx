import React from "react";
import styled from "styled-components";

interface IProps {
  id: string;
}

const Container = styled.div`
  text-align: center;
`;

const ToggleWrapper = styled.div`
  position: relative;
  width: 55px;
  display: inline-block;
  text-align: left;
`;

const Input = styled.input`
  display: none;
  &:checked + Label InnerSpan {
    margin-left: 0%;
  }
  &:checked + Label Span {
    right: 0px;
  }
`;

const Label = styled.label`
  display: block;
  overflow: hidden;
  cursor: pointer;
  border: 0 solid #bbb;
  border-radius: 20px;
`;

const InnerSpan = styled.span`
  display: block;
  width: 200%;
  margin-left: -100%;
  transition: margin 0.3s ease-in 0s;

  &:before,
  &:after {
    float: left;
    width: 50%;
    height: 30px;
    padding: 0;
    line-height: 26px;
    color: #fff;
    font-weight: bold;
    box-sizing: border-box;
  }

  &:before {
    content: "";
    padding-left: 10px;
    background-color: #060;
    color: #fff;
  }
  &:after {
    content: "";
    padding-right: 10px;
    background-color: #bbb;
    color: #fff;
    text-align: right;
  }
`;

const Span = styled.span`
  display: block;
  width: 20px;
  margin: 5px;
  background: #fff;
  position: absolute;
  top: 0;
  bottom: 0;
  //left:0;
  right: 25px;
  border: 0 solid #bbb;
  border-radius: 20px;
  transition: all 0.3s ease-in 0s;
`;

const SwitchButton: React.FC<IProps> = ({ id }) => {
  return (
    <Container>
      <ToggleWrapper>
        <Input type="checkbox" id={id} />
        <Label htmlFor={id}>
          <InnerSpan />
          <Span />
        </Label>
      </ToggleWrapper>
    </Container>
  );
};

export default SwitchButton;
