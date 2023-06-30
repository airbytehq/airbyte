use schemars::JsonSchema;
use serde::Deserialize;
use url::Url;

pub static DEFAULT_API: &str = "https://app.field33.com/api/v1/";

#[derive(JsonSchema, Clone, Debug, Deserialize)]
pub struct Config {
    /// API token, used to communicate with Field33 API. You can generate an API token using the
    /// Field33 app in your Organization settings.
    #[serde(rename = "API Token")]
    pub token: String,
    /// Organization ID to push data into. You can look this up in the Field33 application in your
    /// Organization settings.
    #[serde(rename = "Organization ID")]
    pub organization: String,
    /// Send requests to this API instead. Leave this empty if you are not sure what to
    /// put here.
    #[serde(rename = "API")]
    pub api: Option<Url>,
}

impl Config {
    pub fn url(&self) -> Url {
        self.api.clone().unwrap_or_else(|| {
            DEFAULT_API
                .parse()
                .expect("DEFAULT_API should be a valid URL")
        })
    }
}
