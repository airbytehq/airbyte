import React, { useEffect, useState } from "react";
import styled from "styled-components";

import { Button } from "components";

import { StartIcon, PrevIcon, NextIcon, EndIcon } from "./Icons";

interface IProps {
  pages: number;
  value?: number;
  onChange?: (value: number) => void;
}

interface ButtonProps {
  isSelected?: boolean;
  buttonType?: "start" | "prev" | "page" | "next" | "end";
}

const getBorderRadius = (props: ButtonProps): string => {
  if (props.buttonType === "start") {
    return "6px";
  } else if (props.buttonType === "prev") {
    return "6px 0 0 6px";
  } else if (props.buttonType === "page") {
    return "0";
  } else if (props.buttonType === "next") {
    return "0 6px 6px 0";
  } else if (props.buttonType === "end") {
    return "6px";
  }
  return "6px";
};

const getMargin = (props: ButtonProps): string => {
  if (props.buttonType === "start") {
    return "0 10px 0 0";
  } else if (props.buttonType === "end") {
    return "0 0 0 10px";
  }
  return "0";
};

const Container = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const PageButton = styled(Button)<ButtonProps>`
  min-width: 40px;
  height: 34px;
  background-color: ${({ theme, isSelected }) => (isSelected ? "#EEF2FF" : theme.white)};
  border-top: 1px solid ${({ isSelected }) => (isSelected ? "#6366F1" : "#D1D5DB")};
  border-bottom: 1px solid ${({ isSelected }) => (isSelected ? "#6366F1" : "#D1D5DB")};
  border-left: 1px solid ${({ isSelected }) => (isSelected ? "#6366F1" : "#D1D5DB")};
  border-right: 1px solid ${({ isSelected }) => (isSelected ? "#6366F1" : "#D1D5DB")};
  color: ${({ theme, isSelected }) => (isSelected ? "#6366F1" : theme.textColor)};
  border-radius: ${(props) => getBorderRadius(props)};
  margin: ${(props) => getMargin(props)};
`;

export const Pagination: React.FC<IProps> = ({ pages, value, onChange }) => {
  const formPages = (numberOfPages: number): number[] => {
    const myPages = [];
    for (let index = 0; index < numberOfPages; index++) {
      myPages.push(index + 1);
    }
    return myPages;
  };

  const [currentPage, setCurrentPage] = useState<number>(1);

  useEffect(() => onChange?.(currentPage), [currentPage]);

  useEffect(() => setCurrentPage(value as number), [value]);

  const onPrev = () => {
    setCurrentPage((prev) => {
      if (prev > 1) {
        return prev - 1;
      }
      return prev;
    });
  };

  const onNext = () => {
    setCurrentPage((prev) => {
      if (prev < pages) {
        return prev + 1;
      }
      return prev;
    });
  };

  const onStart = () => setCurrentPage(1);

  const onEnd = () => setCurrentPage(formPages(pages).at(-1) as number);
  if (pages <= 1) {
    return null;
  }
  return (
    <Container>
      <PageButton onClick={onStart} buttonType="start">
        <StartIcon />
      </PageButton>
      <PageButton onClick={onPrev} buttonType="prev">
        <PrevIcon />
      </PageButton>
      {formPages(pages).map((page) => (
        <PageButton isSelected={page === currentPage} onClick={() => setCurrentPage(page)} buttonType="page">
          {page}
        </PageButton>
      ))}
      <PageButton onClick={onNext} buttonType="next">
        <NextIcon />
      </PageButton>
      <PageButton onClick={onEnd} buttonType="end">
        <EndIcon />
      </PageButton>
    </Container>
  );
};
