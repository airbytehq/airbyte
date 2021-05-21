import React from "react";
import styled from "styled-components";
import { FormattedMessage, useIntl } from "react-intl";

import { Input, ControlLabels, DropDown } from "components";

const Content = styled.div`
  display: flex;
  flex-direction: row;
`;

const Column = styled.div`
  flex: 1 0 0;

  &:first-child {
    margin-right: 18px;
  }
`;

const Control = styled.div`
  margin-bottom: 20px;
`;

const TransformationItem: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  // enum with only one value for the moment
  const dropdownData = [{ value: "custom", text: "Custom DBT" }];

  return (
    <Content>
      <Column>
        <Control>
          <ControlLabels
            label={<FormattedMessage id="form.transformationName" />}
          >
            <Input />
          </ControlLabels>
        </Control>
        <Control>
          <ControlLabels label={<FormattedMessage id="form.dockerUrl" />}>
            <Input />
          </ControlLabels>
        </Control>
        <Control>
          <ControlLabels label={<FormattedMessage id="form.repositoryUrl" />}>
            <Input
              placeholder={formatMessage({
                id: "form.repositoryUrl.placeholder",
              })}
            />
          </ControlLabels>
        </Control>
      </Column>

      <Column>
        <Control>
          <ControlLabels
            label={<FormattedMessage id="form.transformationType" />}
          >
            <DropDown
              data={dropdownData}
              placeholder={formatMessage({ id: "form.selectType" })}
            />
          </ControlLabels>
        </Control>
        <Control>
          <ControlLabels
            label={<FormattedMessage id="form.entrypoint" />}
            message={
              <a
                href="https://docs.getdbt.com/reference/dbt-commands"
                target="_blanc"
              >
                <FormattedMessage id="form.entrypoint.docs" />
              </a>
            }
          >
            <Input />
          </ControlLabels>
        </Control>
        <Control>
          <ControlLabels label={<FormattedMessage id="form.gitBranch" />}>
            <Input />
          </ControlLabels>
        </Control>
      </Column>
    </Content>
  );
};

export default TransformationItem;
