import React, { useMemo } from "react";

import { FormBlock } from "core/form/types";
import { PropertySection } from "./PropertySection";
import { useServiceForm } from "../../serviceFormContext";
import { OrderComparator } from "../utils";
import { ConditionSection } from "./ConditionSection";
import { ArraySection } from "./ArraySection";
import { SectionContainer } from "./common";
import { LegacyAuthSection } from "./LegacyAuthSection";

const FormNode: React.FC<{
  sectionPath: string;
  formField: FormBlock;
}> = ({ sectionPath, formField }) => {
  if (formField._type === "formGroup") {
    return (
      <FormSection
        path={sectionPath}
        blocks={formField.properties}
        hasOauth={formField.hasOauth}
      />
    );
  } else if (formField._type === "formCondition") {
    return <ConditionSection path={sectionPath} formField={formField} />;
  } else if (formField._type === "objectArray") {
    return <ArraySection path={sectionPath} formField={formField} />;
  } else if (formField.const !== undefined) {
    return null;
  } else {
    return (
      <SectionContainer>
        <PropertySection property={formField} path={sectionPath} />
      </SectionContainer>
    );
  }
};

const FormSection: React.FC<{
  blocks: FormBlock[] | FormBlock;
  path?: string;
  skipAppend?: boolean;
  hasOauth?: boolean;
}> = ({ blocks = [], path, skipAppend, hasOauth }) => {
  const sections = useMemo(() => {
    const flattenedBlocks = [blocks].flat();

    if (flattenedBlocks.some((b) => Number.isInteger(b.order))) {
      return flattenedBlocks.sort(OrderComparator);
    }

    return flattenedBlocks;
  }, [blocks]);

  const {
    selectedConnector,
    isAuthFlowSelected,
    authFieldsToHide,
  } = useServiceForm();

  return (
    <>
      {hasOauth && <LegacyAuthSection key="authSection" />}
      {sections
        .filter((formField) => !formField.airbyte_hidden)
        // TODO: check that it is a good idea to add authFieldsToHide
        .filter(
          (formField) =>
            !isAuthFlowSelected ||
            (isAuthFlowSelected && !authFieldsToHide.includes(formField.path))
        )
        .map((formField) => {
          const sectionPath = path
            ? skipAppend
              ? path
              : `${path}.${formField.fieldKey}`
            : formField.fieldKey;

          const isAuthSection =
            sectionPath ===
            [
              "connectionConfiguration",
              ...(selectedConnector?.advancedAuth?.predicate_key ?? []),
            ].join(".");

          return (
            <>
              {isAuthSection && isAuthFlowSelected && <LegacyAuthSection />}
              <FormNode
                key={sectionPath}
                formField={formField}
                sectionPath={sectionPath}
              />
            </>
          );
        })}
    </>
  );
};

export { FormSection };
