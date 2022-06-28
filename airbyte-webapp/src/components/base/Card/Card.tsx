import styled from "styled-components";

export const Card = styled.div<{ full?: boolean; $withPadding?: boolean }>`
  width: ${({ full }) => (full ? "100%" : "auto")};
  background: ${({ theme }) => theme.whiteColor};
  border-radius: 10px;
  box-shadow: 0 2px 4px ${({ theme }) => theme.cardShadowColor};
  padding: ${({ $withPadding }) => ($withPadding ? "20px" : undefined)};
  //border: 1px solid ${({ theme }) => theme.greyColor20};
`;
