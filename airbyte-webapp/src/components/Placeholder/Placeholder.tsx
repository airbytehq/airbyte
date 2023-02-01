import React from "react";
import styled from "styled-components";

import { ResourceTypes } from "./types";

interface PlaceholderProps {
  resource: ResourceTypes;
}

const Img = styled.img<PlaceholderProps>`
  max-height: ${({ resource }) =>
    resource === ResourceTypes.Connections ? "465" : resource === ResourceTypes.Destinations ? "409" : "534"}px;
  max-width: 100%;
  margin: 100px auto 0;
  display: block;
`;

const Placeholder: React.FC<PlaceholderProps> = ({ resource }) => {
  return <Img src={`/empty-${resource}.png`} alt="" resource={resource} />;
};

export default Placeholder;
