import { setIn, useFormikContext } from "formik";
import merge from "lodash.merge";
import pick from "lodash.pick";

import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { useRunOauthFlow } from "hooks/services/useConnectorAuth";
import {
  makeConnectionConfigurationPath,
  serverProvidedOauthPaths,
} from "../../../utils";
import { ServiceFormValues } from "../../../types";

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

  const onDone = (completeOauthResponse: Record<string, unknown>) => {
    let newValues: ServiceFormValues;

    if (connector.advancedAuth) {
      const oauthPaths = serverProvidedOauthPaths(connector);

      newValues = Object.entries(oauthPaths).reduce(
        (acc, [key, { path_in_connector_config }]) =>
          setIn(
            acc,
            makeConnectionConfigurationPath(path_in_connector_config),
            completeOauthResponse[key]
          ),
        values
      );
    } else {
      newValues = merge(values, {
        connectionConfiguration: completeOauthResponse,
      });
    }

    setValues(newValues);
  };

  const { run, loading, done } = useRunOauthFlow(connector, onDone);

  return {
    loading,
    done,
    run: async () => {
      const oauthInputFields =
        Object.values(
          connector?.advancedAuth?.oauthConfigSpecification
            ?.oauthUserInputFromConnectorConfigSpecification?.properties ?? {}
        )?.map((property) =>
          makeConnectionConfigurationPath(property.path_in_connector_config)
        ) ?? [];

      if (oauthInputFields.length) {
        oauthInputFields.forEach((path) => setFieldTouched(path, true, true));

        const oAuthErrors = pick(errors, oauthInputFields);

        if (Object.keys(oAuthErrors).length) {
          return;
        }
      }

      const oauthInputParams = pick(values, oauthInputFields);

      await run(oauthInputParams);
    },
  };
}

export { useFormikOauthAdapter };
