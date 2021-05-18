import React from "react";

export type IProps = {
  text?: string;
};

const WithButtonItem: React.FC<IProps> = ({ text }) => {
  return <div>{text}</div>;
};

export default WithButtonItem;
