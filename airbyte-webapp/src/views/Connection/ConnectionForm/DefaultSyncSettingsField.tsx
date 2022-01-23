import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { components } from "react-select";

import { SUPPORTED_MODES } from "./formConfig";
import { DropDown, DropdownProps } from "components";
import { IProps } from "components/base/DropDown/components/SingleValue";
import { OptionView } from "components/base/DropDown/components/Option";

const OptionContent = styled(OptionView)`
  justify-content: left;
  font-size: 12px;
`;

const Title = styled.span`
  color: ${({ theme }) => theme.greyColor55};
  font-size: 11px;
  padding-right: 5px;
`;

const ValueView = styled(components.SingleValue)`
  display: flex;
  align-items: center;
  width: 100%;
  height: 36px;
  padding: 0;
`;

const ValuePart = styled.div`
  flex: 1 0 0;
  vertical-align: center;
  padding: 6px 0 9px;
`;

const OptionValue = styled(ValuePart)`
  padding: 0;
`;

const LastPart = styled(ValuePart)`
  border-left: 2px solid ${({ theme }) => theme.whiteColor};
  padding-left: 9px;
`;

const Mode: React.FC<{
  title: React.ReactNode;
  label: React.ReactNode;
  separator?: string;
}> = (props) => {
  return (
    <>
      <Title> {props.title}:</Title>
      <span>{props.label}</span>
    </>
  );
};

const SingleValue: React.FC<IProps> = (props) => {
  const { syncMode, destinationSyncMode } = props.data.value;
  return (
    <ValueView {...props}>
      <ValuePart>
        <Mode
          title={<FormattedMessage id="connectionForm.sourceTitle" />}
          label={<FormattedMessage id={`syncMode.${syncMode}`} />}
        />
      </ValuePart>
      <LastPart>
        <Mode
          title={<FormattedMessage id="connectionForm.destinationTitle" />}
          label={
            <FormattedMessage
              id={`destinationSyncMode.${destinationSyncMode}`}
            />
          }
        />
      </LastPart>
    </ValueView>
  );
};

const Option: React.FC<any> = (props) => {
  const { syncMode, destinationSyncMode } = props.value;

  return (
    <components.Option {...props}>
      <OptionContent
        data-id={props.data.value}
        isSelected={props.isSelected && !props.isMulti}
      >
        <OptionValue>
          <Mode
            title={<FormattedMessage id="connectionForm.syncType.source" />}
            label={<FormattedMessage id={`syncMode.${syncMode}`} />}
          />
        </OptionValue>
        <OptionValue>
          <Mode
            title={
              <FormattedMessage id="connectionForm.syncType.destination" />
            }
            label={
              <FormattedMessage
                id={`destinationSyncMode.${destinationSyncMode}`}
              />
            }
          />
        </OptionValue>
      </OptionContent>
    </components.Option>
  );
};

const DefaultSyncSettingsField: React.FC<DropdownProps> = (props) => {
  const onChange = (value: any) => {
    console.log(value);
  };

  return (
    <DropDown
      {...props}
      value={{ destinationSyncMode: "append", syncMode: "full_refresh" }}
      components={{
        SingleValue: SingleValue,
        Option: Option,
      }}
      options={SUPPORTED_MODES.map(([syncMode, destinationSyncMode]) => ({
        value: { syncMode, destinationSyncMode },
      }))}
      onChange={onChange}
    />
  );
};

export { DefaultSyncSettingsField };
