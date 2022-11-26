import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Card } from "components";

import { NumberNaming } from "core/functions/numberFormatter";

import Slider from "./components/Slider";
import { PlanDataRowItem } from "./components/Slider";

const CardSeperator = styled.div`
  width: 100%;
  height: 30px;
`;

const Title = styled.div`
  font-weight: 500;
  font-size: 18px;
  line-height: 30px;
  color: ${({ theme }) => theme.black300};
  user-select: none;
`;

const CardContainer = styled.div`
  padding: 10px 20px;
`;

const SliderContainer = styled.div`
  padding: 60px;
`;

const NoteContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-weight: 400;
  font-size: 12px;
  line-height: 30px;
  color: #999999;
`;

const SelectPlanPage: React.FC = () => {
  const [selectedDataRow, setDataRow] = useState<PlanDataRowItem | undefined>();

  const dataRows: PlanDataRowItem[] = [
    { id: "1", numberOfRows: 1 * NumberNaming.M },
    { id: "2", numberOfRows: 2 * NumberNaming.M },
    { id: "3", numberOfRows: 3 * NumberNaming.M },
    { id: "4", numberOfRows: 5 * NumberNaming.M },
    { id: "5", numberOfRows: 10 * NumberNaming.M },
    { id: "6", numberOfRows: 20 * NumberNaming.M },
    { id: "7", numberOfRows: 50 * NumberNaming.M },
    { id: "8", numberOfRows: 100 * NumberNaming.M },
  ];

  return (
    <>
      <Card withPadding roundedBottom>
        <CardContainer>
          <Title>
            <FormattedMessage id="plan.rows.card.title" />
          </Title>
          <SliderContainer>
            <Slider
              min={0}
              max={100 * NumberNaming.M}
              marks={dataRows}
              selectedMark={selectedDataRow}
              onSelect={setDataRow}
            />
          </SliderContainer>
          <NoteContainer>
            <FormattedMessage id="plan.rows.card.note" />
          </NoteContainer>
        </CardContainer>
      </Card>
      <CardSeperator />
      <Card withPadding roundedBottom>
        <CardContainer />
      </Card>
    </>
  );
};

export default SelectPlanPage;
