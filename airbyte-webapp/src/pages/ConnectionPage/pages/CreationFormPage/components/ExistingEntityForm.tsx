import React, { useMemo } from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";
import { Formik, Form, Field, FieldProps } from "formik";
import * as yup from "yup";

import ContentCard from "components/ContentCard";
import { DropDown, Button } from "components/base";
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

const Content = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: row;
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

const ConnectorsDropDown = styled(DropDown)`
  min-width: 50%;
`;

const existingEntityValidationSchema = yup.object().shape({
  entityId: yup.string().required("form.empty.error"),
});

const ExistingEntityForm: React.FC<IProps> = ({ type, onSubmit }) => {
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
        title={
          <Formik
            initialValues={initialValues}
            validationSchema={existingEntityValidationSchema}
            onSubmit={(values: { entityId: string }) => {
              onSubmit(values.entityId);
            }}
          >
            {({ isSubmitting, setFieldValue }) => (
              <Form>
                <Content>
                  <FormattedMessage id={`connectionForm.${type}Existing`} />
                  <Field name="entityId">
                    {({ field }: FieldProps<string>) => (
                      <ConnectorsDropDown
                        {...field}
                        options={dropDownData}
                        onChange={(item: { value: string }) => {
                          setFieldValue(field.name, item.value);
                        }}
                      />
                    )}
                  </Field>
                </Content>
                <BottomBlock>
                  <Button disabled={isSubmitting} type="submit">
                    <FormattedMessage id="form.saveChanges" />
                  </Button>
                </BottomBlock>
              </Form>
            )}
          </Formik>
        }
      />
      <PaddingBlock>
        <FormattedMessage id="onboarding.or" />
      </PaddingBlock>
    </>
  );
};

export default ExistingEntityForm;
