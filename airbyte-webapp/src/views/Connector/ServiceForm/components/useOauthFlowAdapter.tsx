import { useFormikContext } from "formik";
import merge from "lodash.merge";
import pick from "lodash.pick";
// import { flatten } from "flat";

import { ServiceFormValues } from "../types";
import { ConnectorDefinitionSpecification } from "core/domain/connector";
import { useRunOauthFlow } from "hooks/services/useConnectorAuth";

function useFormikOauthAdapter(connector: ConnectorDefinitionSpecification) {
  const {
    values,
    setValues,
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
        connector?.authSpecification?.oauth2Specification?.oauthFlowInputFields?.map(
          (value) => value.join(".")
        ) ?? [];

      if (oauthInputFields.length) {
        // const errors = await validateForm(values);
        //
        // const oAuthErrors = Object.keys(
        //   flatten(errors.connectionConfiguration)
        // ).filter((path) => oauthInputFields.indexOf(path) !== -1);

        if (oauthInputFields.length) {
          // TODO: check if it's easier just to set field as touched by the route and autovalidate
          oauthInputFields.forEach((path) => {
            setFieldTouched(`connectionConfiguration.${path}`, true, true);
          });
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
