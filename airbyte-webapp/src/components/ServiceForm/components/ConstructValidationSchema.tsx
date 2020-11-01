import * as yup from "yup";
import { specification } from "../../../core/resources/SourceDefinitionSpecification";

const ConstructValidationSchema = (
  specifications?: specification,
  properties?: Array<string>
) => {
  const baseValidation = {
    name: yup.string().required("form.empty.error"),
    serviceType: yup.string().required("form.empty.error")
  };

  if (!specifications) {
    return yup.object().shape(baseValidation);
  }

  const getCondition = (propertyKey: string) => {
    const condition = specifications.properties[propertyKey];
    const isRequired = specifications.required.find(
      item => item === propertyKey
    );

    if (condition.type === "string") {
      if (!!isRequired) {
        return yup.string().required("form.empty.error");
      }

      return yup.string();
    }

    if (condition.type === "integer") {
      if (!!isRequired) {
        return yup
          .number()
          .min(condition?.minimum)
          .max(condition?.maximum)
          .required("form.empty.error");
      }

      return yup
        .number()
        .min(condition?.minimum)
        .max(condition?.maximum);
    }

    return null;
  };

  const validationFields = properties
    ? Object.fromEntries([
        ...properties.map(item => [item, getCondition(item)])
      ])
    : null;

  return yup.object().shape({ ...validationFields, ...baseValidation });
};

export default ConstructValidationSchema;
