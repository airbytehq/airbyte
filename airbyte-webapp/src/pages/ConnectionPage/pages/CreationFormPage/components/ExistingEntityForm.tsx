import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { DropDown } from "components";
import { ConnectorIcon } from "components/ConnectorIcon";

import { useDestinationDefinitionList } from "services/connector/DestinationDefinitionService";
import { useSourceDefinitionList } from "services/connector/SourceDefinitionService";

import { useDestinationList } from "../../../../../hooks/services/useDestinationHook";
import { useSourceList } from "../../../../../hooks/services/useSourceHook";

interface IProps {
  type: "source" | "destination";
  onSubmit: (id: string) => void;
  value: string;
  placeholder?: string;
}

const Container = styled.div`
  max-width: 900px;
  margin: 0 auto;
`;

const FormTitle = styled.div`
  font-size: 18px;
  line-height: 24px;
  color: #27272a;
  font-weight: 500;
  margin: 38px 0 20px 0;
`;

const ExistingEntityForm: React.FC<IProps> = ({ type, onSubmit, value, placeholder }) => {
  const { sources } = useSourceList();
  const { sourceDefinitions } = useSourceDefinitionList();
  const { destinations } = useDestinationList();
  const { destinationDefinitions } = useDestinationDefinitionList();

  const dropDownData = useMemo(() => {
    if (type === "source") {
      return sources.map((item) => {
        const sourceDef = sourceDefinitions.find((sd) => sd.sourceDefinitionId === item.sourceDefinitionId);
        return {
          label: item.name,
          value: item.sourceId,
          img: <ConnectorIcon icon={sourceDef?.icon} />,
        };
      });
    }
    return destinations.map((item) => {
      const destinationDef = destinationDefinitions.find(
        (dd) => dd.destinationDefinitionId === item.destinationDefinitionId
      );
      return {
        label: item.name,
        value: item.destinationId,
        img: <ConnectorIcon icon={destinationDef?.icon} />,
      };
    });
  }, [type]);

  if (!dropDownData.length) {
    return null;
  }

  return (
    <Container>
      <FormTitle>
        <FormattedMessage id={`form.select.existing.${type}`} />
      </FormTitle>
      <DropDown
        $background="white"
        $withBorder
        value={value}
        options={dropDownData}
        placeholder={placeholder}
        onChange={(item: { value: string }) => {
          onSubmit(item.value);
        }}
      />
    </Container>
  );
};

export default ExistingEntityForm;
