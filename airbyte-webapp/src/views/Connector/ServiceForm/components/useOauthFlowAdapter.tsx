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
    setFieldTouched,
    errors,
  } = useFormikContext<ServiceFormValues>();

  const onDone = (v: Pick<ServiceFormValues, "connectionConfiguration">) =>
    setValues(merge(values, v));

  const { run, loading, done } = useRunOauthFlow(connector, onDone);

  return {
    loading,
    done,
    run: async () => {
      const oauthInputFields =
        connector?.authSpecification?.oauth2Specification?.oauthFlowInputFields?.map(
          (value) => value.join(".")
        ) ?? [];

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
