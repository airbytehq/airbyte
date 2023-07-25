use crate::apis::InterceptorStream;
use crate::libs::json::{create_root_schema, tokenize_jsonpointer};

use crate::errors::Error;
use crate::libs::airbyte_catalog::{
    self, ConfiguredCatalog, ConfiguredStream, DestinationSyncMode, Range, ResourceSpec, Status,
    SyncMode,
};
use crate::libs::command::READY;
use crate::libs::stream::{get_airbyte_response, get_decoded_message, stream_airbyte_responses};

use bytes::Bytes;
use proto_flow::capture::{request, response};
use proto_flow::capture::{Request, Response};
use proto_flow::flow::ConnectorState;

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;

use validator::Validate;

use futures::{stream, StreamExt};
use serde_json as sj;
use serde_json::value::RawValue;
use std::fs::File;
use std::io::Write;
use tempfile::{Builder, TempDir};

use json_patch::merge;

use super::fix_document_schema::{
    fix_document_schema_keys, fix_nonstandard_jsonschema_attributes, remove_enums,
    normalize_schema_date_to_datetime
};
use super::normalize::{automatic_normalizations, normalize_doc, NormalizationEntry};
use super::remap::remap;

const PROTOCOL_VERSION: u32 = 3032023;

const CONFIG_FILE_NAME: &str = "config.json";
const CATALOG_FILE_NAME: &str = "catalog.json";
const STATE_FILE_NAME: &str = "state.json";

const SPEC_PATCH_FILE_NAME: &str = "spec.patch.json";
const SPEC_MAP_FILE_NAME: &str = "spec.map.json";
const OAUTH2_PATCH_FILE_NAME: &str = "oauth2.patch.json";
const DOC_URL_PATCH_FILE_NAME: &str = "documentation_url.patch.json";
const SCHEMA_NORMALIZATIONS_FILE_NAME: &str = "schema_normalizations.json";
const STREAM_PATCH_DIR_NAME: &str = "streams";
const STREAM_PK_SUFFIX: &str = ".pk.json";
const STREAM_PATCH_SUFFIX: &str = ".patch.json";
const STREAM_NORMALIZE_SUFFIX: &str = ".normalize.json";
const SELECTED_STREAMS_FILE_NAME: &str = "selected_streams.json";

// SavedBinding records the binding index and applicable normalizations obtained from a Pull
// request.
struct SavedBinding {
    i: usize,
    normalizations: Option<Vec<NormalizationEntry>>,
    doc_schema: serde_json::Value,
}

pub struct AirbyteSourceInterceptor {
    validate_request: Arc<Mutex<Option<request::Validate>>>,
    stream_to_binding: Arc<Mutex<HashMap<String, SavedBinding>>>,
    tmp_dir: TempDir,
}

impl AirbyteSourceInterceptor {
    pub fn new() -> Self {
        AirbyteSourceInterceptor {
            validate_request: Arc::new(Mutex::new(None)),
            stream_to_binding: Arc::new(Mutex::new(HashMap::new())),
            tmp_dir: Builder::new()
                .prefix("atf-")
                .tempdir_in("/var/tmp")
                .expect("failed to create temp dir."),
        }
    }

    fn adapt_spec_request_stream(&mut self, _request: request::Spec) -> InterceptorStream {
        Box::pin(stream::once(async move { Ok(Bytes::from(READY)) }))
    }

    fn adapt_spec_response_stream(&mut self, in_stream: InterceptorStream) -> InterceptorStream {
        Box::pin(stream::once(async {
            let message = get_airbyte_response(in_stream, |m| m.spec.is_some(), "spec").await?;
            let spec = message.spec.unwrap();
            let mut endpoint_spec = sj::from_str::<sj::Value>(spec.connection_specification.get())?;
            let mut auth_spec = spec
                .auth_specification
                .map(|aspec| sj::from_str::<sj::Value>(aspec.get()))
                .transpose()?;

            let spec_patch = std::fs::read_to_string(SPEC_PATCH_FILE_NAME)
                .ok()
                .map(|p| sj::from_str::<sj::Value>(&p))
                .transpose()?;
            let oauth2_patch = std::fs::read_to_string(OAUTH2_PATCH_FILE_NAME)
                .ok()
                .map(|p| sj::from_str::<sj::Value>(&p))
                .transpose()?;
            let documentation_url_patch = std::fs::read_to_string(DOC_URL_PATCH_FILE_NAME)
                .ok()
                .map(|p| sj::from_str::<sj::Value>(&p))
                .transpose()?;

            if let Some(p) = spec_patch {
                merge(&mut endpoint_spec, &p);
            }

            if let Some(p) = oauth2_patch.as_ref() {
                auth_spec = Some(p.clone());
            }

            let documentation_url = match documentation_url_patch {
                Some(p) => p
                    .get("documentation_url")
                    .map(|v| v.as_str())
                    .flatten()
                    .map(|s| s.to_string()),
                None => spec.documentation_url,
            };

            fix_nonstandard_jsonschema_attributes(&mut endpoint_spec);

            let v = serde_json::to_vec(&Response {
                spec: Some(response::Spec {
                    protocol: PROTOCOL_VERSION,
                    config_schema_json: endpoint_spec.to_string(),
                    resource_config_schema_json: serde_json::to_string(&create_root_schema::<
                        ResourceSpec,
                    >())?,
                    oauth2: auth_spec
                        .map(|spec| serde_json::from_value(spec))
                        .transpose()?,
                    documentation_url: documentation_url.unwrap_or_default(),
                }),
                ..Default::default()
            })?;

            Ok(v.into())
        }))
    }

    fn adapt_config_json(config_json: &str) -> Result<sj::Value, Error> {
        let spec_map = std::fs::read_to_string(SPEC_MAP_FILE_NAME)
            .ok()
            .map(|p| sj::from_str::<sj::Value>(&p))
            .transpose()?;
        let mut spec = sj::from_str::<sj::Value>(config_json)?;
        if let Some(mapping) = spec_map.as_ref() {
            remap(&mut spec, &mapping)?;
        }

        Ok(spec)
    }

    fn adapt_discover_request(
        &mut self,
        config_file_path: String,
        request: request::Discover,
    ) -> InterceptorStream {
        Box::pin(stream::once(async move {
            let config_json = AirbyteSourceInterceptor::adapt_config_json(&request.config_json)?;

            File::create(config_file_path)?.write_all(config_json.to_string().as_bytes())?;

            Ok(Bytes::from(READY))
        }))
    }

    fn adapt_discover_response_stream(
        &mut self,
        in_stream: InterceptorStream,
    ) -> InterceptorStream {
        Box::pin(stream::once(async {
            let message =
                get_airbyte_response(in_stream, |m| m.catalog.is_some(), "catalog").await?;
            let catalog = message.catalog.unwrap();

            let selected_streams_option = std::fs::read_to_string(SELECTED_STREAMS_FILE_NAME)
                .ok()
                .map(|p| sj::from_str::<Vec<String>>(&p))
                .transpose()?;

            let schema_normalizations = std::fs::read_to_string(SCHEMA_NORMALIZATIONS_FILE_NAME)
                .ok()
                .map(|p| sj::from_str::<Vec<String>>(&p))
                .transpose()?.unwrap_or(Vec::new());

            let mut resp = response::Discovered::default();
            for stream in catalog.streams {
                let mut disable = false;
                if let Some(ref selected_streams) = selected_streams_option {
                    if !selected_streams.contains(&stream.name) {
                        disable = true;
                    }
                }

                let has_incremental = stream
                    .supported_sync_modes
                    .map(|modes| modes.contains(&SyncMode::Incremental))
                    .unwrap_or(false);
                let mode = if has_incremental {
                    SyncMode::Incremental
                } else {
                    SyncMode::FullRefresh
                };

                let mut key: Vec<String> = stream
                    .source_defined_primary_key
                    .unwrap_or(Vec::new())
                    .iter()
                    .map(|key| {
                        doc::Pointer::from_iter(key.iter().map(|s| doc::ptr::Token::from_str(&s)))
                            .to_string()
                    })
                    .collect();

                let recommended_name = stream_to_recommended_name(&stream.name);

                let doc_pk = std::fs::read_to_string(format!(
                    "{}/{}{}",
                    STREAM_PATCH_DIR_NAME, recommended_name, STREAM_PK_SUFFIX
                ))
                .or_else(|_| {
                    std::fs::read_to_string(format!(
                        "{}/*{}",
                        STREAM_PATCH_DIR_NAME, STREAM_PK_SUFFIX
                    ))
                })
                .ok()
                .map(|p| sj::from_str::<sj::Value>(&p))
                .transpose()?;
                if let Some(p) = doc_pk {
                    key = p
                        .as_array()
                        .ok_or(Error::InvalidPKPatch("expected an array".to_string()))?
                        .into_iter()
                        .map(|s| format!("/{}", s.as_str().unwrap()))
                        .collect();
                }

                // cursor_field does not accept JSON Pointers, but keys directly, so we remove the initial `/` from keys
                let non_pointer_key = key.iter().map(|ptr| ptr.get(1..).unwrap().to_string()).collect();

                // Sometimes the cursor_field is Some([]), this block handles that case and defaults to the primary key
                let cursor_field = if let Some(cf) = stream.default_cursor_field {
                    if cf.is_empty() {
                        Some(non_pointer_key)
                    } else {
                        Some(cf)
                    }
                } else {
                    Some(non_pointer_key)
                };

                let resource_spec = ResourceSpec {
                    stream: stream.name.clone(),
                    namespace: stream.namespace,
                    sync_mode: mode,
                    cursor_field,
                };

                let mut doc_schema = sj::from_str::<sj::Value>(stream.json_schema.get())?;

                let doc_schema_patch = std::fs::read_to_string(format!(
                    "{}/{}{}",
                    STREAM_PATCH_DIR_NAME, recommended_name, STREAM_PATCH_SUFFIX
                ))
                .or_else(|_| {
                    std::fs::read_to_string(format!(
                        "{}/*{}",
                        STREAM_PATCH_DIR_NAME, STREAM_PATCH_SUFFIX
                    ))
                })
                .ok()
                .map(|p| sj::from_str::<sj::Value>(&p))
                .transpose()?;

                if let Some(p) = doc_schema_patch {
                    merge(&mut doc_schema, &p);
                }

                fix_nonstandard_jsonschema_attributes(&mut doc_schema);
                remove_enums(&mut doc_schema);

                for normalization in &schema_normalizations {
                    match normalization.as_str() {
                        "date-to-datetime" => {
                            normalize_schema_date_to_datetime(&mut doc_schema);
                        },
                        _ => {}
                    }
                }

                resp.bindings.push(response::discovered::Binding {
                    recommended_name,
                    resource_config_json: serde_json::to_string(&resource_spec)?,
                    key: key.clone(),
                    document_schema_json: fix_document_schema_keys(doc_schema, key)?.to_string(),
                    disable,
                })
            }

            let v = serde_json::to_vec(&Response {
                discovered: Some(resp),
                ..Default::default()
            })?;
            Ok(v.into())
        }))
    }

    fn adapt_validate_request_stream(
        &mut self,
        config_file_path: String,
        validate_request: Arc<Mutex<Option<request::Validate>>>,
        request: request::Validate,
    ) -> InterceptorStream {
        Box::pin(stream::once(async move {
            *validate_request.lock().await = Some(request.clone());

            let config_json = AirbyteSourceInterceptor::adapt_config_json(&request.config_json)?;

            File::create(config_file_path)?.write_all(config_json.to_string().as_bytes())?;

            Ok(Bytes::from(READY))
        }))
    }

    fn adapt_validate_response_stream(
        &mut self,
        validate_request: Arc<Mutex<Option<request::Validate>>>,
        in_stream: InterceptorStream,
    ) -> InterceptorStream {
        Box::pin(stream::once(async move {
            let message = get_airbyte_response(
                in_stream,
                |m| m.connection_status.is_some(),
                "connection status",
            )
            .await?;

            let connection_status = message.connection_status.unwrap();

            if connection_status.status != Status::Succeeded {
                let msg = connection_status.message.unwrap_or("".to_string());
                return Err(Error::ConnectionStatusUnsuccessful(msg));
            }

            let req = validate_request.lock().await;
            let req = req.as_ref().ok_or(Error::MissingValidateRequest)?;
            let mut resp = response::Validated::default();
            for binding in &req.bindings {
                let resource: ResourceSpec = serde_json::from_str(&binding.resource_config_json)?;
                resp.bindings.push(response::validated::Binding {
                    resource_path: vec![resource.stream],
                });
            }

            let v = serde_json::to_vec(&Response {
                validated: Some(resp),
                ..Default::default()
            })?;
            Ok(v.into())
        }))
    }

    fn adapt_apply_request_stream(&mut self, _request: request::Apply) -> InterceptorStream {
        Box::pin(stream::once(async move { Ok(Bytes::from(READY)) }))
    }

    fn adapt_apply_response_stream(&mut self, in_stream: InterceptorStream) -> InterceptorStream {
        Box::pin(stream::once(async {
            // TODO(johnny): Due to the current factoring, we invoke the connector with `spec`
            // and discard its response. This is a bit silly.
            _ = get_airbyte_response(in_stream, |m| m.spec.is_some(), "spec").await?;

            let v = serde_json::to_vec(&Response {
                applied: Some(response::Applied::default()),
                ..Default::default()
            })?;
            Ok(v.into())
        }))
    }

    fn adapt_pull_request_stream(
        &mut self,
        config_file_path: String,
        catalog_file_path: String,
        state_file_path: String,
        stream_to_binding: Arc<Mutex<HashMap<String, SavedBinding>>>,
        open: request::Open,
    ) -> InterceptorStream {
        Box::pin(stream::once(async move {
            File::create(state_file_path.clone())?.write_all(&open.state_json.as_bytes())?;
            let c = open.capture.unwrap();

            let config_json = AirbyteSourceInterceptor::adapt_config_json(&c.config_json)?;

            File::create(config_file_path.clone())?
                .write_all(config_json.to_string().as_bytes())?;

            let mut catalog = ConfiguredCatalog {
                streams: Vec::new(),
                range: open.range.as_ref().map(|r| Range {
                    begin: r.key_begin,
                    end: r.key_end,
                }),
            };

            for (i, binding) in c.bindings.iter().enumerate() {
                let resource: ResourceSpec = serde_json::from_str(&binding.resource_config_json)?;

                let normalizations = std::fs::read_to_string(format!(
                    "{}/{}{}",
                    STREAM_PATCH_DIR_NAME, &resource.stream, STREAM_NORMALIZE_SUFFIX
                ))
                .ok()
                .map(|p| sj::from_str::<Vec<NormalizationEntry>>(&p))
                .transpose()?;

                let mut projections = HashMap::new();
                if let Some(ref collection) = binding.collection {
                    stream_to_binding.lock().await.insert(
                        resource.stream.clone(),
                        SavedBinding {
                            i,
                            normalizations,
                            doc_schema: serde_json::from_str(&collection.write_schema_json)?,
                        },
                    );
                    for p in &collection.projections {
                        projections.insert(p.field.clone(), p.ptr.clone());
                    }

                    let primary_key: Vec<Vec<String>> = collection
                        .key
                        .iter()
                        .map(|ptr| tokenize_jsonpointer(ptr))
                        .collect();
                    catalog.streams.push(ConfiguredStream {
                        sync_mode: resource.sync_mode.clone(),
                        destination_sync_mode: DestinationSyncMode::Append,
                        cursor_field: resource.cursor_field,
                        primary_key: Some(primary_key),
                        stream: airbyte_catalog::Stream {
                            name: resource.stream,
                            namespace: resource.namespace,
                            json_schema: RawValue::from_string(
                                collection.write_schema_json.clone(),
                            )?,
                            supported_sync_modes: Some(vec![resource.sync_mode.clone()]),
                            default_cursor_field: None,
                            source_defined_cursor: None,
                            source_defined_primary_key: None,
                        },
                        projections,
                    });
                }
            }

            if let Err(e) = catalog.validate() {
                return Err(Error::InvalidCatalog(e));
            }

            serde_json::to_writer(File::create(catalog_file_path.clone())?, &catalog)?;

            Ok(Bytes::from(READY))
        }))
    }

    fn adapt_pull_response_stream(
        &mut self,
        stream_to_binding: Arc<Mutex<HashMap<String, SavedBinding>>>,
        in_stream: InterceptorStream,
    ) -> InterceptorStream {
        // Respond first with Opened.
        let opened = stream::once(async {
            let v = serde_json::to_vec(&Response {
                opened: Some(Default::default()),
                ..Default::default()
            })?;
            Ok(v.into())
        });

        // Then stream airbyte messages converted to the native protocol.
        let airbyte_message_stream = Box::pin(stream_airbyte_responses(in_stream));
        let airbyte_message_stream = stream::try_unfold(
            (stream_to_binding, airbyte_message_stream),
            |(stb, mut stream)| async move {
                let message = match stream.next().await {
                    Some(m) => m?,
                    None => {
                        return Ok(None);
                    }
                };

                let mut resp = Response::default();
                if let Some(state) = message.state {
                    resp.checkpoint = Some(response::Checkpoint {
                        state: Some(ConnectorState {
                            updated_json: state.data.get().to_string(),
                            merge_patch: state.merge.unwrap_or(false),
                        }),
                    });

                    let v = serde_json::to_vec(&resp)?;
                    Ok(Some((v.into(), (stb, stream))))
                } else if let Some(mut record) = message.record {
                    let mut stream_to_binding = stb.lock().await;
                    let binding = stream_to_binding
                        .get_mut(&record.stream)
                        .ok_or(Error::DanglingConnectorRecord(record.stream.clone()))?;

                    automatic_normalizations(&mut record.data, &mut binding.doc_schema);
                    normalize_doc(&mut record.data, &binding.normalizations);

                    resp.captured = Some(response::Captured {
                        binding: binding.i as u32,
                        doc_json: record.data.to_string(),
                    });
                    drop(stream_to_binding);

                    let v = serde_json::to_vec(&resp)?;
                    Ok(Some((v.into(), (stb, stream))))
                } else {
                    Err(Error::InvalidPullResponse)
                }
            },
        );

        Box::pin(opened.chain(airbyte_message_stream))
    }

    fn input_file_path(&mut self, file_name: &str) -> String {
        self.tmp_dir
            .path()
            .join(file_name)
            .to_str()
            .expect("failed construct config file name.")
            .into()
    }
}

#[derive(Clone, PartialEq)]
pub enum Operation {
    Spec,
    Discover,
    Validate,
    Apply,
    Capture,
}

impl AirbyteSourceInterceptor {
    // Looks at the first request to determine the operation, and gives back the stream that will
    // include the first request as well
    pub async fn first_request(
        &mut self,
        in_stream: InterceptorStream,
    ) -> Result<(Operation, Request), Error> {
        let first_req = get_decoded_message::<Request>(in_stream).await?;

        if first_req.spec.is_some() {
            Ok((Operation::Spec, first_req))
        } else if first_req.discover.is_some() {
            Ok((Operation::Discover, first_req))
        } else if first_req.validate.is_some() {
            Ok((Operation::Validate, first_req))
        } else if first_req.apply.is_some() {
            Ok((Operation::Apply, first_req))
        } else if first_req.open.is_some() {
            Ok((Operation::Capture, first_req))
        } else {
            Err(Error::UnknownOperation(format!("{:#?}", first_req)))
        }
    }

    pub fn adapt_command_args(&mut self, op: &Operation) -> Vec<String> {
        let config_file_path = self.input_file_path(CONFIG_FILE_NAME);
        let catalog_file_path = self.input_file_path(CATALOG_FILE_NAME);
        let state_file_path = self.input_file_path(STATE_FILE_NAME);

        let airbyte_args = match op {
            Operation::Spec => vec!["spec"],
            Operation::Discover => vec!["discover", "--config", &config_file_path],
            Operation::Validate => vec!["check", "--config", &config_file_path],
            // TODO(johnny): These are effective no-ops, but as-written must invoke the connector.
            // We should refactor this.
            Operation::Apply => vec!["spec"],
            Operation::Capture => {
                vec![
                    "read",
                    "--config",
                    &config_file_path,
                    "--catalog",
                    &catalog_file_path,
                    "--state",
                    &state_file_path,
                ]
            }
        };

        airbyte_args.into_iter().map(|s| s.to_string()).collect()
    }

    pub fn adapt_request_stream(
        &mut self,
        op: &Operation,
        first_request: Request,
    ) -> Result<InterceptorStream, Error> {
        let config_file_path = self.input_file_path(CONFIG_FILE_NAME);
        let catalog_file_path = self.input_file_path(CATALOG_FILE_NAME);
        let state_file_path = self.input_file_path(STATE_FILE_NAME);

        match op {
            Operation::Spec => Ok(self.adapt_spec_request_stream(first_request.spec.unwrap())),
            Operation::Discover => {
                Ok(self.adapt_discover_request(config_file_path, first_request.discover.unwrap()))
            }
            Operation::Validate => Ok(self.adapt_validate_request_stream(
                config_file_path,
                Arc::clone(&self.validate_request),
                first_request.validate.unwrap(),
            )),
            // TODO(johnny): These are effective no-ops, but as-written must invoke the connector.
            // We should refactor this.
            Operation::Apply => Ok(self.adapt_apply_request_stream(first_request.apply.unwrap())),
            Operation::Capture => Ok(self.adapt_pull_request_stream(
                config_file_path,
                catalog_file_path,
                state_file_path,
                Arc::clone(&self.stream_to_binding),
                first_request.open.unwrap(),
            )),
        }
    }

    pub fn adapt_response_stream(
        &mut self,
        op: &Operation,
        in_stream: InterceptorStream,
    ) -> Result<InterceptorStream, Error> {
        match op {
            Operation::Spec => Ok(self.adapt_spec_response_stream(in_stream)),
            Operation::Discover => Ok(self.adapt_discover_response_stream(in_stream)),
            Operation::Validate => {
                Ok(self
                    .adapt_validate_response_stream(Arc::clone(&self.validate_request), in_stream))
            }
            Operation::Apply => Ok(self.adapt_apply_response_stream(in_stream)),
            Operation::Capture => {
                Ok(self.adapt_pull_response_stream(Arc::clone(&self.stream_to_binding), in_stream))
            }
        }
    }
}

// stream names have no constraints.
// Strip and sanitize them to be valid collection names.
fn stream_to_recommended_name(stream: &str) -> String {
    stream
        .split('/')
        .map(|chunk| {
            chunk
                .chars()
                .filter(|c| c.is_alphanumeric() || *c == '-' || *c == '.' || *c == '_')
                .collect()
        })
        .filter(|c: &String| !c.is_empty())
        .collect::<Vec<_>>()
        .join("/")
}

#[cfg(test)]
mod test {
    use super::stream_to_recommended_name;

    #[test]
    fn test_stream_to_recommended_name() {
        assert_eq!(stream_to_recommended_name("Hello-World"), "Hello-World");
        assert_eq!(
            stream_to_recommended_name("/&foo!/B ar// b+i-n.g /"),
            "foo/Bar/bi-n.g"
        );
    }
}
