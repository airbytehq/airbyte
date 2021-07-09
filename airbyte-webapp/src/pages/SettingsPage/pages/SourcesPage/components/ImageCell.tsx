import React from "react";
import styled from "styled-components";

type IProps = {
  imageName: string;
  link: string;
};

const Link = styled.a`
  height: 17px;
  margin-right: 9px;
  color: ${({ theme }) => theme.darkPrimaryColor};

  &:hover,
  &:active {
    color: ${({ theme }) => theme.primaryColor};
  }
`;

const ImageCell: React.FC<IProps> = ({ imageName, link }) => {
  return (
    <Link href={link} target="_blank">
      {imageName}
    </Link>
  );
};

export default ImageCell;
