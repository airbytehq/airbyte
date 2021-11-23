import {FormattedMessage} from "react-intl";
import {Button} from "../../../../components/base/Button";
import React from "react";

export <Button isLoading={loading} type="button" onClick={run}>
    {done ? (
        <FormattedMessage id="connectorForm.reauthenticate" />
    ) : (
        <FormattedMessage
            id="connectorForm.authenticate"
            values={{ connector: selectedService?.name }}
        />
    )}
</Button>
