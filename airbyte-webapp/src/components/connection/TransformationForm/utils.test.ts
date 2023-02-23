import merge from "lodash/merge";
import { InferType, ValidationError } from "yup";

import { validationSchema } from "./utils";

describe("<TransformationForm /> - validationSchema", () => {
  const customTransformationFields: InferType<typeof validationSchema> = {
    name: "test name",
    operatorConfiguration: {
      dbt: {
        gitRepoUrl: "https://github.com/username/example.git",
        dockerImage: "image",
        dbtArguments: "arguments",
        gitRepoBranch: "",
      },
    },
  };

  it("should successfully validate the schema", async () => {
    const result = validationSchema.validate(customTransformationFields);

    await expect(result).resolves.toBeTruthy();
  });

  it("should fail if 'name' is empty", async () => {
    await expect(async () => {
      await validationSchema.validateAt(
        "name",
        merge(customTransformationFields, {
          name: "",
        })
      );
    }).rejects.toThrow(ValidationError);
  });

  it("should fail if 'gitRepoUrl' is invalid", async () => {
    await expect(async () => {
      await validationSchema.validateAt(
        "operatorConfiguration.dbt.gitRepoUrl",
        merge(customTransformationFields, {
          operatorConfiguration: { dbt: { gitRepoUrl: "" } },
        })
      );
    }).rejects.toThrow(ValidationError);

    await expect(async () => {
      await validationSchema.validateAt(
        "operatorConfiguration.dbt.gitRepoUrl",
        merge(customTransformationFields, {
          operatorConfiguration: { dbt: { gitRepoUrl: "https://github.com/username/example.git   " } },
        })
      );
    }).rejects.toThrow(ValidationError);

    await expect(async () => {
      await validationSchema.validateAt(
        "operatorConfiguration.dbt.gitRepoUrl",
        merge(customTransformationFields, {
          operatorConfiguration: { dbt: { gitRepoUrl: "https://github.com/username/example.git/" } },
        })
      );
    }).rejects.toThrow(ValidationError);
  });

  it("should fail if 'dockerImage' is empty", async () => {
    await expect(async () => {
      await validationSchema.validateAt(
        "operatorConfiguration.dbt.dockerImage",
        merge(customTransformationFields, {
          operatorConfiguration: { dbt: { dockerImage: "" } },
        })
      );
    }).rejects.toThrow(ValidationError);
  });

  it("should fail if 'dbtArguments' is empty", async () => {
    await expect(async () => {
      await validationSchema.validateAt(
        "operatorConfiguration.dbt.dbtArguments",
        merge(customTransformationFields, {
          operatorConfiguration: { dbt: { dbtArguments: "" } },
        })
      );
    }).rejects.toThrow(ValidationError);
  });
});
