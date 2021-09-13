import React, { useState } from 'react'
import { FormattedMessage } from 'react-intl'

import ContentCard from '@app/components/ContentCard'
import ServiceForm from '@app/views/Connector/ServiceForm'
import useRouter from '@app/hooks/useRouter'
import { useSourceDefinitionSpecificationLoad } from '@app/hooks/services/useSourceHook'
import { JobInfo } from '@app/core/resources/Scheduler'
import { JobsLogItem } from '@app/components/JobItem'
import { createFormErrorMessage } from '@app/utils/errorStatusMessage'
import { ConnectionConfiguration } from '@app/core/domain/connection'
import { SourceDefinition } from '@app/core/resources/SourceDefinition'
import { useAnalytics } from '@app/hooks/useAnalytics'

type IProps = {
    onSubmit: (values: {
        name: string
        serviceType: string
        sourceDefinitionId?: string
        connectionConfiguration?: ConnectionConfiguration
    }) => void
    afterSelectConnector?: () => void
    sourceDefinitions: SourceDefinition[]
    hasSuccess?: boolean
    error?: { message?: string; status?: number } | null
    jobInfo?: JobInfo
}

const SourceForm: React.FC<IProps> = ({
    onSubmit,
    sourceDefinitions,
    error,
    hasSuccess,
    jobInfo,
    afterSelectConnector,
}) => {
    const { location } = useRouter()
    const analyticsService = useAnalytics()

    const [sourceDefinitionId, setSourceDefinitionId] = useState(
        location.state?.sourceDefinitionId || ''
    )
    const { sourceDefinitionSpecification, isLoading } =
        useSourceDefinitionSpecificationLoad(sourceDefinitionId)
    const onDropDownSelect = (sourceDefinitionId: string) => {
        setSourceDefinitionId(sourceDefinitionId)
        const connector = sourceDefinitions.find(
            (item) => item.sourceDefinitionId === sourceDefinitionId
        )

        if (afterSelectConnector) {
            afterSelectConnector()
        }

        analyticsService.track('New Source - Action', {
            action: 'Select a connector',
            connector_source_definition: connector?.name,
            connector_source_definition_id: sourceDefinitionId,
        })
    }

    const onSubmitForm = async (values: {
        name: string
        serviceType: string
    }) => {
        await onSubmit({
            ...values,
            sourceDefinitionId:
                sourceDefinitionSpecification?.sourceDefinitionId,
        })
    }

    const errorMessage = error ? createFormErrorMessage(error) : null

    return (
        <ContentCard title={<FormattedMessage id="onboarding.sourceSetUp" />}>
            <ServiceForm
                onServiceSelect={onDropDownSelect}
                onSubmit={onSubmitForm}
                formType="source"
                availableServices={sourceDefinitions}
                specifications={
                    sourceDefinitionSpecification?.connectionSpecification
                }
                documentationUrl={
                    sourceDefinitionSpecification?.documentationUrl
                }
                hasSuccess={hasSuccess}
                errorMessage={errorMessage}
                isLoading={isLoading}
                formValues={
                    sourceDefinitionId
                        ? { serviceType: sourceDefinitionId, name: '' }
                        : undefined
                }
                allowChangeConnector
            />
            <JobsLogItem jobInfo={jobInfo} />
        </ContentCard>
    )
}

export default SourceForm
