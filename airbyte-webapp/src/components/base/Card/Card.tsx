import styled from "styled-components";

export const Card = styled.div<{ full?: boolean }>`
  width: ${({ full }) => (full ? "100%" : "auto")};
  background: ${({ theme }) => theme.whiteColor};
  border-radius: 10px;
  box-shadow: 0 2px 4px ${({ theme }) => theme.cardShadowColor};
  //border: 1px solid ${({ theme }) => theme.greyColor20};
`;
