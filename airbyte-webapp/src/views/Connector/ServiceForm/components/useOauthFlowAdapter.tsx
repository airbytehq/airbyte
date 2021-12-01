import { useFormikContext } from "formik";
import merge from "lodash.merge";
import pick from "lodash.pick";

import { ServiceFormValues } from "../types";
import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { useRunOauthFlow } from "hooks/services/useConnectorAuth";

function useFormikOauthAdapter(
  connector: ConnectorDefinitionSpecification
): {
  loading: boolean;
  done?: boolean;
  run: () => Promise<void>;
} {
  const {
    values,
    setValues,
    errors,
    setFieldTouched,
  } = useFormikContext<ServiceFormValues>();

  const onDone = (v: Pick<ServiceFormValues, "connectionConfiguration">) =>
    setValues(merge(values, v));

  const { run, loading, done } = useRunOauthFlow(connector, onDone);

  return {
    loading,
    done,
    run: async () => {
      const oauthInputFields =
        Object.values(
          connector?.advancedAuth?.oauth_config_specification
            ?.oauthUserInputFromConnectorConfigSpecification?.properties ?? {}
        )?.map((property) => property.path_in_connector_config.join(".")) ?? [];

      if (oauthInputFields.length) {
        oauthInputFields.forEach((path) =>
          setFieldTouched(`connectionConfiguration.${path}`, true, true)
        );

        const oAuthErrors = pick(
          errors.connectionConfiguration,
          oauthInputFields
        );

        if (Object.keys(oAuthErrors).length) {
          return;
        }
      }

      const oauthInputParams = pick(
        values.connectionConfiguration,
        oauthInputFields
      );

      await run(oauthInputParams);
    },
  };
}

export { useFormikOauthAdapter };
