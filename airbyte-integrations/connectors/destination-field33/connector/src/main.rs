use airbyte_protocol::{
    async_trait,
    types::{AirbyteCatalog, AirbyteRecordMessage},
    Connector, TargetConnector,
};
use anyhow::{anyhow, Result};
use reqwest::Client;
use serde_json::{to_string, Value};
use std::collections::HashMap;
use tokio::sync::Mutex;

mod config;

pub struct Field33Connector {
    data: Mutex<HashMap<String, Vec<Value>>>,
    client: Client,
}

impl Field33Connector {
    pub fn new() -> Self {
        Self {
            data: Mutex::new(HashMap::new()),
            client: Client::default(),
        }
    }
}

impl Connector for Field33Connector {
    type Config = config::Config;
}

#[async_trait]
impl TargetConnector for Field33Connector {
    async fn write_record(
        &self,
        config: &Self::Config,
        catalog: &AirbyteCatalog,
        record: AirbyteRecordMessage,
    ) -> Result<()> {
        let mut data = self.data.lock().await;
        let name = if let Some(namespace) = &record.namespace {
            format!("{namespace}_{}", record.stream)
        } else {
            record.stream
        };
        let list = data.entry(name).or_default();
        list.push(record.data);
        Ok(())
    }

    async fn write_finish(&self, config: &Self::Config, catalog: &AirbyteCatalog) -> Result<()> {
        let data = self.data.lock().await;
        let api = config.url();
        for (stream, items) in data.iter() {
            let url = api.join(&format!(
                "organizations/{}/jsonlimport/{}",
                config.organization, stream
            ))?;

            // serialize items as JSONL
            let mut body = Vec::new();
            for item in items {
                jsonl::write(&mut body, item)?;
            }

            let response = self
                .client
                .post(url.as_str())
                .bearer_auth(&config.token)
                .body(body)
                .send()
                .await?;

            if !response.status().is_success() {
                return Err(anyhow!("Error uploading data: {}", response.text().await?));
            }
        }
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    Field33Connector::new().main().await?;
    Ok(())
}
