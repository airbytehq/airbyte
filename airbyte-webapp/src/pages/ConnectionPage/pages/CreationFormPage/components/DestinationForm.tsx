import React, { useState } from 'react'
import { useResource } from 'rest-hooks'

import useRouter from '@app/hooks/useRouter'
import DestinationDefinitionResource from '@app/core/resources/DestinationDefinition'
import useDestination from '@app/hooks/services/useDestinationHook'

// TODO: create separate component for source and destinations forms
import DestinationForm from '@app/pages/DestinationPage/pages/CreateDestinationPage/components/DestinationForm'
import { ConnectionConfiguration } from '@app/core/domain/connection'
import useWorkspace from '@app/hooks/services/useWorkspace'

type IProps = {
    afterSubmit: () => void
}

const CreateDestinationPage: React.FC<IProps> = ({ afterSubmit }) => {
    const { push, location } = useRouter()
    const { workspace } = useWorkspace()
    const [successRequest, setSuccessRequest] = useState(false)
    const [errorStatusRequest, setErrorStatusRequest] = useState(null)

    const { destinationDefinitions } = useResource(
        DestinationDefinitionResource.listShape(),
        {
            workspaceId: workspace.workspaceId,
        }
    )
    const { createDestination } = useDestination()

    const onSubmitDestinationForm = async (values: {
        name: string
        serviceType: string
        connectionConfiguration?: ConnectionConfiguration
    }) => {
        setErrorStatusRequest(null)

        const connector = destinationDefinitions.find(
            (item) => item.destinationDefinitionId === values.serviceType
        )
        try {
            const result = await createDestination({
                values,
                destinationConnector: connector,
            })
            setSuccessRequest(true)
            setTimeout(() => {
                setSuccessRequest(false)
                push({
                    state: {
                        ...(location.state as Record<string, unknown>),
                        destinationId: result.destinationId,
                    },
                })
                afterSubmit()
            }, 2000)
        } catch (e) {
            setErrorStatusRequest(e)
        }
    }

    return (
        <DestinationForm
            onSubmit={onSubmitDestinationForm}
            destinationDefinitions={destinationDefinitions}
            hasSuccess={successRequest}
            error={errorStatusRequest}
        />
    )
}

export default CreateDestinationPage
