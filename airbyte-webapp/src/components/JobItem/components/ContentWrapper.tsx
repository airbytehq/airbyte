import React from "react";
import pose from "react-pose";

type IProps = {
  children?: React.ReactNode;
  isOpen?: boolean;
};

const itemConfig = {
  open: {
    height: "auto",
    opacity: 1,
    transition: "tween",
  },
  closed: {
    height: "1px",
    opacity: 0,
    transition: "tween",
  },
};

const ContentWrapperElement = pose.div(itemConfig);

const ContentWrapper: React.FC<IProps> = ({ children, isOpen }) => {
  return (
    <ContentWrapperElement pose={!isOpen ? "closed" : "open"} withParent={false}>
      {children}
    </ContentWrapperElement>
  );
};

export default ContentWrapper;
