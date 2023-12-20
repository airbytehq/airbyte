import { Grid } from "@mui/material";
import React from "react";
import styled from "styled-components";

import { Connector, ConnectorDefinition } from "core/domain/connector";

import DataCard from "./components/Card";
interface SourcePanelProps {
  value?: string;
  onSelect: (data: ConnectorDefinition) => void;
  type: "source" | "destination";
  data: ConnectorDefinition[];
  title?: string;
}

export const Container = styled.div`
  max-width: 900px;
  margin: 60px auto 120px auto;
`;

export const Title = styled.div`
  font-weight: 500;
  font-size: 18px;
  line-height: 30px;
  color: #27272a;
  margin-bottom: 30px;
`;

export const DataCardList = styled.div`
  display: flex;
  // flex-wrap: wrap;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 44px 94px;
  @media (max-width: 1008px) {
    grid-template-columns: repeat(3, 1fr);
  }
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    grid-row-gap: 10px;
  }
`;

const DefinitionCard: React.FC<SourcePanelProps> = ({ data, onSelect, value, title, type }) => {
  return (
    <Container>
      <Title>{title}</Title>
      <Grid container spacing={{ lg: 5, md: 4, sm: 5, xs: 4 }}>
        {data.map((item) => (
          <Grid item lg={3} md={4} sm={4} xs={3}>
            <DataCard
              type={type}
              data={item}
              key={Connector.id(item)}
              onClick={onSelect}
              checked={Connector.id(item) === value}
            />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default DefinitionCard;
