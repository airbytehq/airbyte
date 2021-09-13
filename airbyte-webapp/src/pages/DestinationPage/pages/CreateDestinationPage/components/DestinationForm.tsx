import React, { useState } from 'react'
import { FormattedMessage } from 'react-intl'

import ContentCard from '@app/components/ContentCard'
import ServiceForm from '@app/views/Connector/ServiceForm'
import useRouter from '@app/hooks/useRouter'
import { useDestinationDefinitionSpecificationLoad } from '@app/hooks/services/useDestinationHook'
import { JobInfo } from '@app/core/resources/Scheduler'
import { JobsLogItem } from '@app/components/JobItem'
import { createFormErrorMessage } from '@app/utils/errorStatusMessage'
import { ConnectionConfiguration } from '@app/core/domain/connection'
import { DestinationDefinition } from '@app/core/resources/DestinationDefinition'
import { useAnalytics } from '@app/hooks/useAnalytics'

type IProps = {
  onSubmit: (values: {
    name: string
    serviceType: string
    destinationDefinitionId?: string
    connectionConfiguration?: ConnectionConfiguration
  }) => void
  destinationDefinitions: DestinationDefinition[]
  hasSuccess?: boolean
  error?: { message?: string; status?: number } | null
  jobInfo?: JobInfo
  afterSelectConnector?: () => void
}

const DestinationForm: React.FC<IProps> = ({
  onSubmit,
  destinationDefinitions,
  error,
  hasSuccess,
  jobInfo,
  afterSelectConnector,
}) => {
  const { location } = useRouter()
  const analyticsService = useAnalytics()

  const [destinationDefinitionId, setDestinationDefinitionId] = useState(
    location.state?.destinationDefinitionId || ''
  )
  const { destinationDefinitionSpecification, isLoading } =
    useDestinationDefinitionSpecificationLoad(destinationDefinitionId)
  const onDropDownSelect = (destinationDefinitionId: string) => {
    setDestinationDefinitionId(destinationDefinitionId)
    const connector = destinationDefinitions.find(
      (item) => item.destinationDefinitionId === destinationDefinitionId
    )

    if (afterSelectConnector) {
      afterSelectConnector()
    }

    analyticsService.track('New Destination - Action', {
      action: 'Select a connector',
      connector_destination_definition: connector?.name,
      connector_destination_definition_id: destinationDefinitionId,
    })
  }

  const onSubmitForm = async (values: {
    name: string
    serviceType: string
  }) => {
    await onSubmit({
      ...values,
      destinationDefinitionId:
        destinationDefinitionSpecification?.destinationDefinitionId,
    })
  }

  const errorMessage = error ? createFormErrorMessage(error) : null

  return (
    <ContentCard title={<FormattedMessage id="onboarding.destinationSetUp" />}>
      <ServiceForm
        onServiceSelect={onDropDownSelect}
        onSubmit={onSubmitForm}
        formType="destination"
        availableServices={destinationDefinitions}
        specifications={
          destinationDefinitionSpecification?.connectionSpecification
        }
        documentationUrl={destinationDefinitionSpecification?.documentationUrl}
        hasSuccess={hasSuccess}
        errorMessage={errorMessage}
        isLoading={isLoading}
        formValues={
          destinationDefinitionId
            ? { serviceType: destinationDefinitionId }
            : undefined
        }
        allowChangeConnector
      />
      <JobsLogItem jobInfo={jobInfo} />
    </ContentCard>
  )
}

export default DestinationForm
