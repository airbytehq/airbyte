import React, { useState } from 'react'
import styled from 'styled-components'
import { FormattedMessage } from 'react-intl'
import { useResource } from 'rest-hooks'

import { Source } from '@app/core/resources/Source'
import ContentCard from '@app/components/ContentCard'
import ServiceForm from '@app/views/Connector/ServiceForm'
import useSource from '@app/hooks/services/useSourceHook'
import SourceDefinitionSpecificationResource from '@app/core/resources/SourceDefinitionSpecification'
import DeleteBlock from '@app/components/DeleteBlock'
import { Connection } from '@app/core/resources/Connection'
import { JobInfo } from '@app/core/resources/Scheduler'
import { JobsLogItem } from '@app/components/JobItem'
import { createFormErrorMessage } from '@app/utils/errorStatusMessage'
import { ConnectionConfiguration } from '@app/core/domain/connection'
import SourceDefinitionResource from '@app/core/resources/SourceDefinition'

const Content = styled.div`
    max-width: 813px;
    margin: 18px auto;
`

type IProps = {
    currentSource: Source
    connectionsWithSource: Connection[]
}

const SourceSettings: React.FC<IProps> = ({
    currentSource,
    connectionsWithSource,
}) => {
    const [saved, setSaved] = useState(false)
    const [errorStatusRequest, setErrorStatusRequest] = useState<{
        statusMessage: string | React.ReactNode
        response: JobInfo
    } | null>(null)

    const { updateSource, deleteSource, checkSourceConnection } = useSource()

    const sourceDefinitionSpecification = useResource(
        SourceDefinitionSpecificationResource.detailShape(),
        {
            sourceDefinitionId: currentSource.sourceDefinitionId,
        }
    )
    const sourceDefinition = useResource(
        SourceDefinitionResource.detailShape(),
        {
            sourceDefinitionId: currentSource.sourceDefinitionId,
        }
    )

    const onSubmit = async (values: {
        name: string
        serviceType: string
        connectionConfiguration?: ConnectionConfiguration
    }) => {
        setErrorStatusRequest(null)
        try {
            await updateSource({
                values,
                sourceId: currentSource.sourceId,
            })

            setSaved(true)
        } catch (e) {
            const errorStatusMessage = createFormErrorMessage(e)

            setErrorStatusRequest({ ...e, statusMessage: errorStatusMessage })
        }
    }

    const onRetest = async (values: {
        name: string
        serviceType: string
        connectionConfiguration?: ConnectionConfiguration
    }) => {
        setErrorStatusRequest(null)
        try {
            await checkSourceConnection({
                values,
                sourceId: currentSource.sourceId,
            })
            setSaved(true)
        } catch (e) {
            const errorStatusMessage = createFormErrorMessage(e)

            setErrorStatusRequest({ ...e, statusMessage: errorStatusMessage })
        }
    }

    const onDelete = async () => {
        await deleteSource({ connectionsWithSource, source: currentSource })
    }

    return (
        <Content>
            <ContentCard
                title={<FormattedMessage id="sources.sourceSettings" />}
            >
                <ServiceForm
                    onRetest={onRetest}
                    isEditMode
                    onSubmit={onSubmit}
                    formType="source"
                    availableServices={[sourceDefinition]}
                    successMessage={
                        saved && <FormattedMessage id="form.changesSaved" />
                    }
                    errorMessage={errorStatusRequest?.statusMessage}
                    formValues={{
                        ...currentSource,
                        serviceType: currentSource.sourceDefinitionId,
                    }}
                    specifications={
                        sourceDefinitionSpecification?.connectionSpecification
                    }
                />
                <JobsLogItem jobInfo={errorStatusRequest?.response} />
            </ContentCard>
            <DeleteBlock type="source" onDelete={onDelete} />
        </Content>
    )
}

export default SourceSettings
