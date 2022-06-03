import React from "react";
import styled from "styled-components";

type ImageCellProps = {
  imageName: string;
  link: string | undefined;
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

const ImageCell: React.FC<ImageCellProps> = ({ imageName, link }) => {
  return (
    <Link href={link} target="_blank">
      {imageName}
    </Link>
  );
};

export default ImageCell;
