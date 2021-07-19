import React from "react";
import { components } from "react-select";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Cell } from "components/SimpleTableComponents";
import { DropDown, DropdownProps } from "components";
import Text from "components/base/DropDown/components/Text";
import { IProps } from "components/base/DropDown/components/SingleValue";
import { OptionView } from "components/base/DropDown/components/Option";

const SingleValue: React.FC<IProps> = (props) => {
  const { syncMode, destinationSyncMode } = props.data.value;
  return (
    <Text fullText>
      <components.SingleValue {...props}>
        <FormattedMessage id={`syncMode.${syncMode}`} /> |{" "}
        <FormattedMessage id={`destinationSyncMode.${destinationSyncMode}`} />
      </components.SingleValue>
    </Text>
  );
};

const Title = styled.span`
  color: ${({ theme }) => theme.greyColor20};
`;

const Label = styled.span``;

const Mode: React.FC<{
  title: React.ReactNode;
  label: React.ReactNode;
  separator?: string;
}> = (props) => {
  return (
    <>
      <Title> {props.title}:</Title>
      <Label>
        {props.label} {props.separator ? props.separator : null}
      </Label>
    </>
  );
};

const Option: React.FC<any> = (props) => {
  const { syncMode, destinationSyncMode } = props.value;

  return (
    <components.Option {...props}>
      <OptionView
        data-id={props.data.value}
        isSelected={props.isSelected && !props.isMulti}
      >
        <Mode
          title={<FormattedMessage id="connectionForm.syncType.source" />}
          label={<FormattedMessage id={`syncMode.${syncMode}`} />}
          separator="|"
        />
        <Mode
          title={<FormattedMessage id="connectionForm.syncType.destination" />}
          label={
            <FormattedMessage
              id={`destinationSyncMode.${destinationSyncMode}`}
            />
          }
        />
      </OptionView>
    </components.Option>
  );
};

const SyncSettingsCell: React.FC<DropdownProps> = (props) => {
  return (
    <Cell flex={1.5}>
      <DropDown
        {...props}
        components={{
          SingleValue: SingleValue,
          Option: Option,
        }}
        withBorder
        isSearchable={false}
      />
    </Cell>
  );
};

export { SyncSettingsCell };
