import React, { useMemo } from "react";
import styled from "styled-components";
import { FormattedMessage, useIntl } from "react-intl";
import { useResource } from "rest-hooks";
import { Formik, Form, Field, FieldProps } from "formik";
import * as yup from "yup";

import ContentCard from "components/ContentCard";
import { DropDown, Button, ControlLabels } from "components";
import useWorkspace from "hooks/services/useWorkspace";
import SourceResource from "core/resources/Source";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import DestinationResource from "core/resources/Destination";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";
import ImageBlock from "components/ImageBlock";

type IProps = {
  type: "source" | "destination";
  onSubmit: (id: string) => void;
};

const FormContent = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const BottomBlock = styled.div`
  text-align: right;
  margin-top: 34px;
`;

const PaddingBlock = styled.div`
  text-align: center;
  padding: 18px 0 15px;
  font-weight: 500;
  font-size: 15px;
  line-height: 18px;
`;

const existingEntityValidationSchema = yup.object().shape({
  entityId: yup.string().required("form.empty.error"),
});

const ExistingEntityForm: React.FC<IProps> = ({ type, onSubmit }) => {
  const formatMessage = useIntl().formatMessage;
  const { workspace } = useWorkspace();

  const { sources } = useResource(SourceResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
  const { sourceDefinitions } = useResource(
    SourceDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );

  const { destinations } = useResource(DestinationResource.listShape(), {
    workspaceId: workspace.workspaceId,
  });
  const { destinationDefinitions } = useResource(
    DestinationDefinitionResource.listShape(),
    {
      workspaceId: workspace.workspaceId,
    }
  );

  const dropDownData = useMemo(() => {
    if (type === "source") {
      return sources.map((item) => {
        const sourceDef = sourceDefinitions.find(
          (sd) => sd.sourceDefinitionId === item.sourceDefinitionId
        );
        return {
          label: item.name,
          value: item.sourceId,
          img: <ImageBlock img={sourceDef?.icon} />,
        };
      });
    } else {
      return destinations.map((item) => {
        const destinationDef = destinationDefinitions.find(
          (dd) => dd.destinationDefinitionId === item.destinationDefinitionId
        );
        return {
          label: item.name,
          value: item.destinationId,
          img: <ImageBlock img={destinationDef?.icon} />,
        };
      });
    }
  }, [type]);

  if (!dropDownData.length) {
    return null;
  }

  const initialValues = { entityId: "" };
  return (
    <>
      <ContentCard
        title={<FormattedMessage id={`connectionForm.${type}Existing`} />}
      >
        <Formik
          initialValues={initialValues}
          validationSchema={existingEntityValidationSchema}
          onSubmit={(values: { entityId: string }) => {
            onSubmit(values.entityId);
          }}
        >
          {({ isSubmitting, setFieldValue }) => (
            <FormContent>
              <Field name="entityId">
                {({ field }: FieldProps<string>) => (
                  <ControlLabels
                    label={formatMessage({
                      id: `connectionForm.${type}Title`,
                    })}
                  >
                    <DropDown
                      {...field}
                      options={dropDownData}
                      onChange={(item: { value: string }) => {
                        setFieldValue(field.name, item.value);
                      }}
                    />
                  </ControlLabels>
                )}
              </Field>
              <BottomBlock>
                <Button disabled={isSubmitting} type="submit">
                  <FormattedMessage id={`connectionForm.${type}Use`} />
                </Button>
              </BottomBlock>
            </FormContent>
          )}
        </Formik>
      </ContentCard>
      <PaddingBlock>
        <FormattedMessage id="onboarding.or" />
      </PaddingBlock>
    </>
  );
};

export default ExistingEntityForm;
