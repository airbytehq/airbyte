import React from "react";

import styled from "./ResetStreamDetails.module.scss";

interface IProps {
  names: string[];
}

export const ResetStreamsDetails: React.FC<IProps> = ({ names }) => (
  <p className={styled.textContainer}>
    {names.map((name) => (
      <span className={styled.text}>{name}</span>
    ))}
  </p>
);
