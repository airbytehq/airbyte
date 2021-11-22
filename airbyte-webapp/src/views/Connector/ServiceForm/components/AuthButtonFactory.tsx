import { Button } from "../../../../components/base/Button";
import { FormattedMessage } from "react-intl";
import { ConnectorDefinition } from "../../../../core/domain/connector";
import { isSourceDefinition } from "../../../../core/domain/connector/source";
import { isDestinationDefinition } from "../../../../core/domain/connector/destination";

const getButton = (
  loading: boolean,
  run: () => void,
  selectedService?: ConnectorDefinition,
  done?: boolean
): JSX.Element => {
  let definitionId = "";
  if (selectedService && isSourceDefinition(selectedService)) {
    definitionId = selectedService.sourceDefinitionId;
  } else if (selectedService && isDestinationDefinition(selectedService)) {
    definitionId = selectedService.destinationDefinitionId;
  } else {
    throw new Error(`Unrecognized service type. Service: ${selectedService}`);
  }

  switch (definitionId) {
    case "253487c0-2246-43ba-a21f-5116b20a2c50": // google ads
    case "eff3616a-f9c3-11eb-9a03-0242ac130003": // google analytics
    case "d19ae824-e289-4b14-995a-0632eb46d246": // google directory
    case "eb4c9e00-db83-4d63-a386-39cfa91012a8": // google search console
    case "71607ba1-c0ac-4799-8049-7f4b90dd50f7": // google sheets
    case "ed9dfefa-1bbc-419d-8c5e-4d78f0ef6734": // google workspace admin reports
      return (
        <Button isLoading={loading} type="button" onClick={run} iconOnly>
          {
            <img
              src="/connectors/google/btn_google_signin_dark_normal_web@2x.png"
              height={40}
              alt={"Sign in with google"}
            />
          }
        </Button>
      );
    default:
      return (
        <Button isLoading={loading} type="button" onClick={run}>
          {done ? (
            <>
              <FormattedMessage id="connectorForm.reauthenticate" />
            </>
          ) : (
            <FormattedMessage
              id="connectorForm.authenticate"
              values={{ connector: selectedService?.name }}
            />
          )}
        </Button>
      );
  }
};

export default getButton;
