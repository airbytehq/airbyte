import React from "react";
// import styled from "styled-components";

import { Card } from "components";

interface IProps {
  title?: string | React.ReactNode;
  className?: string;
  onClick?: () => void;
  full?: boolean;
  light?: boolean;
}

const ContentCard: React.FC<IProps> = (props) => <Card>{props.children}</Card>;

export default ContentCard;
