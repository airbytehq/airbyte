import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";

import ImageBlock from "components/ImageBlock";

type ConnectionCellProps = {
  sourceDefinitionName: string;
  destinationDefinitionName: string;
  sourceIcon?: string;
  destinationIcon?: string;
};

const Icon = styled(ImageBlock)`
  margin-right: 12px;
  display: inline-block;
  vertical-align: middle;
  height: 20px;
  width: 20px;
`;

const Connector = styled.div`
  font-weight: 500;
  font-size: 14px;
  line-height: 25px;
`;

const Arrow = styled(FontAwesomeIcon)`
  margin: 0 17px 0 9px;
  font-size: 9px;
`;

const ConnectionCell: React.FC<ConnectionCellProps> = ({
  sourceDefinitionName,
  destinationDefinitionName,
  sourceIcon,
  destinationIcon,
}) => {
  return (
    <>
      <Connector>
        <Icon small img={sourceIcon} />
        {sourceDefinitionName}
      </Connector>
      <Connector>
        <Arrow icon={faArrowRight} />
        <Icon small img={destinationIcon} />
        {destinationDefinitionName}
      </Connector>
    </>
  );
};

export default ConnectionCell;
