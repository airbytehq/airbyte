import React from 'react'
import { useEffect, useState } from 'react'

const registry_url =
  'https://connectors.airbyte.com/files/generated_reports/connector_registry_report.json'

async function fetchCatalog(url, setter) {
  const response = await fetch(url)
  const registry = await response.json()
  setter(registry)
}

export default function ConnectorStats({ definitionId }) {
  const [registry, setRegistry] = useState([])
  const [connector, setConnector] = useState({})

  useEffect(() => {
    fetchCatalog(registry_url, setRegistry)
  }, [])

  useEffect(() => {
    setConnector(registry.filter((c) => c.definitionId === definitionId)[0])
  }, [registry, definitionId])

  if (registry.length === 0 || !connector)
    return <div>{`Loading connector stats...`}</div>

  return (
    <>
      <div>
        Is Available on OSS: {connector.is_oss ? '✅' : '❌'} - Is Available on
        Cloud:
        {connector.is_cloud ? '✅' : '❌'}
      </div>
      <div>
        Current Build Status:{' '}
        <img
          src={`https://img.shields.io/endpoint?url=${connector.test_summary_url}/badge.json`}
          alt='Current Build Status'
        />
      </div>
    </>
  )
}
