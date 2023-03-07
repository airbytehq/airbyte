use crate::apis::{FlowCaptureOperation, InterceptorStream};
use crate::libs::json::{create_root_schema, tokenize_jsonpointer};

use crate::errors::Error;
use crate::libs::airbyte_catalog::{
    self, ConfiguredCatalog, ConfiguredStream, DestinationSyncMode, Range, ResourceSpec, Status,
    SyncMode,
};
use crate::libs::command::READY;
use crate::libs::protobuf::encode_message;
use crate::libs::stream::{
    get_airbyte_response, get_decoded_message, stream_airbyte_responses, stream_runtime_messages,
};

use bytes::Bytes;
use proto_flow::capture::{
    discover_response, validate_response, ApplyRequest, ApplyResponse, DiscoverRequest,
    DiscoverResponse, Documents, PullRequest, PullResponse, SpecRequest, SpecResponse,
    ValidateRequest, ValidateResponse,
};
use proto_flow::flow::{DriverCheckpoint, Slice};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;

use validator::Validate;

use futures::{stream, StreamExt, TryStreamExt};
use serde_json as sj;
use serde_json::value::RawValue;
use std::fs::File;
use std::io::Write;
use tempfile::{Builder, TempDir};

use json_patch::merge;

use super::fix_document_schema::fix_document_schema_keys;
use super::remap::remap;

const CONFIG_FILE_NAME: &str = "config.json";
const CATALOG_FILE_NAME: &str = "catalog.json";
const STATE_FILE_NAME: &str = "state.json";

const SPEC_PATCH_FILE_NAME: &str = "spec.patch.json";
const SPEC_MAP_FILE_NAME: &str = "spec.map.json";
const OAUTH2_PATCH_FILE_NAME: &str = "oauth2.patch.json";
const DOC_URL_PATCH_FILE_NAME: &str = "documentation_url.patch.json";
const STREAM_PATCH_DIR_NAME: &str = "streams";
const STREAM_PK_SUFFIX: &str = ".pk.json";
const STREAM_PATCH_SUFFIX: &str = ".patch.json";
const SELECTED_STREAMS_FILE_NAME: &str = "selected_streams.json";

pub struct AirbyteSourceInterceptor {
    validate_request: Arc<Mutex<Option<ValidateRequest>>>,
    stream_to_binding: Arc<Mutex<HashMap<String, usize>>>,
    tmp_dir: TempDir,
}

impl AirbyteSourceInterceptor {
    pub fn new() -> Self {
        AirbyteSourceInterceptor {
            validate_request: Arc::new(Mutex::new(None)),
            stream_to_binding: Arc::new(Mutex::new(HashMap::new())),
            tmp_dir: Builder::new()
                .prefix("airbyte-source-")
                .tempdir_in("/var/tmp")
                .expect("failed to create temp dir."),
        }
    }

    fn adapt_spec_request_stream(&mut self, in_stream: InterceptorStream) -> InterceptorStream {
        Box::pin(stream::once(async move {
            get_decoded_message::<SpecRequest>(in_stream).await?;
            Ok(Bytes::from(READY))
        }))
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

            encode_message(&SpecResponse {
                endpoint_spec_schema_json: endpoint_spec.to_string(),
                resource_spec_schema_json: serde_json::to_string_pretty(&create_root_schema::<
                    ResourceSpec,
                >())?,
                oauth2_spec: auth_spec
                    .map(|spec| serde_json::from_value(spec))
                    .transpose()?,
                documentation_url: documentation_url.unwrap_or_default(),
            })
        }))
    }

    fn adapt_endpoint_spec(endpoint_spec_json: &str) -> Result<sj::Value, Error> {
        let spec_map = std::fs::read_to_string(SPEC_MAP_FILE_NAME)
            .ok()
            .map(|p| sj::from_str::<sj::Value>(&p))
            .transpose()?;
        let mut spec = sj::from_str::<sj::Value>(endpoint_spec_json)?;
        if let Some(mapping) = spec_map.as_ref() {
            remap(&mut spec, &mapping)?;
        }

        Ok(spec)
    }

    fn adapt_discover_request(
        &mut self,
        config_file_path: String,
        in_stream: InterceptorStream,
    ) -> InterceptorStream {
        Box::pin(stream::once(async move {
            let request = get_decoded_message::<DiscoverRequest>(in_stream).await?;
            let endpoint_spec_json =
                AirbyteSourceInterceptor::adapt_endpoint_spec(&request.endpoint_spec_json)?;

            File::create(config_file_path)?.write_all(endpoint_spec_json.to_string().as_bytes())?;

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

            let mut resp = DiscoverResponse::default();
            for stream in catalog.streams {
                if let Some(ref selected_streams) = selected_streams_option {
                    if !selected_streams.contains(&stream.name) {
                        continue;
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
                let resource_spec = ResourceSpec {
                    stream: stream.name.clone(),
                    namespace: stream.namespace,
                    sync_mode: mode,
                    cursor_field: stream.default_cursor_field,
                };

                let mut source_defined_primary_key =
                    stream.source_defined_primary_key.unwrap_or(Vec::new());

                let recommended_name = stream_to_recommended_name(&stream.name);

                let doc_pk = std::fs::read_to_string(format!(
                    "{}/{}{}",
                    STREAM_PATCH_DIR_NAME, recommended_name, STREAM_PK_SUFFIX
                ))
                .ok()
                .map(|p| sj::from_str::<sj::Value>(&p))
                .transpose()?;
                if let Some(p) = doc_pk {
                    source_defined_primary_key = p
                        .as_array()
                        .ok_or(Error::InvalidPKPatch("expected an array".to_string()))?
                        .into_iter()
                        .map(|s| {
                            s.as_str()
                                .unwrap()
                                .split('/')
                                .map(|a| a.to_owned())
                                .collect()
                        })
                        .collect();
                }

                let key_ptrs = source_defined_primary_key
                    .iter()
                    .map(|k| doc::Pointer::from_vec(k).to_string())
                    .collect();

                let mut doc_schema = sj::from_str::<sj::Value>(stream.json_schema.get())?;
                let doc_schema_patch = std::fs::read_to_string(format!(
                    "{}/{}{}",
                    STREAM_PATCH_DIR_NAME, recommended_name, STREAM_PATCH_SUFFIX
                ))
                .ok()
                .map(|p| sj::from_str::<sj::Value>(&p))
                .transpose()?;

                if let Some(p) = doc_schema_patch {
                    merge(&mut doc_schema, &p);
                }

                resp.bindings.push(discover_response::Binding {
                    recommended_name,
                    resource_spec_json: serde_json::to_string(&resource_spec)?,
                    key_ptrs,
                    document_schema_json: fix_document_schema_keys(
                        doc_schema,
                        source_defined_primary_key,
                    )?
                    .to_string(),
                })
            }

            encode_message(&resp)
        }))
    }

    fn adapt_validate_request_stream(
        &mut self,
        config_file_path: String,
        validate_request: Arc<Mutex<Option<ValidateRequest>>>,
        in_stream: InterceptorStream,
    ) -> InterceptorStream {
        Box::pin(stream::once(async move {
            let request = get_decoded_message::<ValidateRequest>(in_stream).await?;
            *validate_request.lock().await = Some(request.clone());

            let endpoint_spec_json =
                AirbyteSourceInterceptor::adapt_endpoint_spec(&request.endpoint_spec_json)?;

            File::create(config_file_path)?.write_all(endpoint_spec_json.to_string().as_bytes())?;

            Ok(Bytes::from(READY))
        }))
    }

    fn adapt_validate_response_stream(
        &mut self,
        validate_request: Arc<Mutex<Option<ValidateRequest>>>,
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
            let mut resp = ValidateResponse::default();
            for binding in &req.bindings {
                let resource: ResourceSpec = serde_json::from_str(&binding.resource_spec_json)?;
                resp.bindings.push(validate_response::Binding {
                    resource_path: vec![resource.stream],
                });
            }

            encode_message(&resp)
        }))
    }

    fn adapt_apply_request_stream(&mut self, in_stream: InterceptorStream) -> InterceptorStream {
        Box::pin(stream::once(async move {
            get_decoded_message::<ApplyRequest>(in_stream).await?;
            Ok(Bytes::from(READY))
        }))
    }

    fn adapt_apply_response_stream(&mut self, in_stream: InterceptorStream) -> InterceptorStream {
        Box::pin(stream::once(async {
            // TODO(johnny): Due to the current factoring, we invoke the connector with `spec`
            // and discard its response. This is a bit silly.
            _ = get_airbyte_response(in_stream, |m| m.spec.is_some(), "spec").await?;

            encode_message(&ApplyResponse::default())
        }))
    }

    fn adapt_pull_request_stream(
        &mut self,
        config_file_path: String,
        catalog_file_path: String,
        state_file_path: String,
        stream_to_binding: Arc<Mutex<HashMap<String, usize>>>,
        in_stream: InterceptorStream,
    ) -> InterceptorStream {
        let runtime_messages_stream = Box::pin(stream_runtime_messages::<PullRequest>(in_stream));
        Box::pin(
            stream::try_unfold((stream_to_binding, runtime_messages_stream, config_file_path, catalog_file_path, state_file_path),
            |(stb, mut stream, config_file_path, catalog_file_path, state_file_path)| async move {
                let mut request = match stream.next().await {
                    Some(m) => m?,
                    None => {
                        return Ok(None);
                    }
                };
                if let Some(ref mut o) = request.open {
                    File::create(state_file_path.clone())?.write_all(&o.driver_checkpoint_json)?;

                    if let Some(ref mut c) = o.capture {
                        let endpoint_spec_json = AirbyteSourceInterceptor::adapt_endpoint_spec(&c.endpoint_spec_json)?;

                        File::create(config_file_path.clone())?.write_all(endpoint_spec_json.to_string().as_bytes())?;

                        let mut catalog = ConfiguredCatalog {
                            streams: Vec::new(),
                            tail: o.tail,
                            range: Range {
                                begin: o.key_begin,
                                end: o.key_end,
                            },
                        };

                        for (i, binding) in c.bindings.iter().enumerate() {
                            let resource: ResourceSpec =
                                serde_json::from_str(&binding.resource_spec_json)?;
                            stb.lock().await.insert(resource.stream.clone(), i);

                            let mut projections = HashMap::new();
                            if let Some(ref collection) = binding.collection {
                                for p in &collection.projections {
                                    projections.insert(p.field.clone(), p.ptr.clone());
                                }

                                let primary_key: Vec<Vec<String>> = collection
                                    .key_ptrs
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
                                            collection.schema_json.clone(),
                                        )?,
                                        supported_sync_modes: Some(vec![resource
                                            .sync_mode
                                            .clone()]),
                                        default_cursor_field: None,
                                        source_defined_cursor: None,
                                        source_defined_primary_key: None,
                                    },
                                    projections,
                                });
                            }
                        }

                        if let Err(e) = catalog.validate() {
                            return Err(Error::InvalidCatalog(e))
                        }

                        serde_json::to_writer(File::create(catalog_file_path.clone())?, &catalog)?
                    }

                    Ok(Some((Some(Bytes::from(READY)), (stb, stream, config_file_path, catalog_file_path, state_file_path))))
                } else {
                    // If we return Ok(None), we will stop consuming the input, but we want to
                    // continue consuming input since we can receive ACK requests from runtime and
                    // we need to consume those to avoid an accumulation of those requests in stdin
                    Ok(Some((None, (stb, stream, config_file_path, catalog_file_path, state_file_path))))
                }
            }).try_filter_map(|item| futures::future::ok(item))
        )
    }

    fn adapt_pull_response_stream(
        &mut self,
        stream_to_binding: Arc<Mutex<HashMap<String, usize>>>,
        in_stream: InterceptorStream,
    ) -> InterceptorStream {
        // Respond first with Opened.
        let opened = stream::once(async {
            encode_message(&PullResponse {
                opened: Some(Default::default()),
                ..Default::default()
            })
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

                let mut resp = PullResponse::default();
                if let Some(state) = message.state {
                    resp.checkpoint = Some(DriverCheckpoint {
                        driver_checkpoint_json: state.data.get().as_bytes().to_vec(),
                        rfc7396_merge_patch: state.merge.unwrap_or(false),
                    });

                    Ok(Some((encode_message(&resp)?, (stb, stream))))
                } else if let Some(record) = message.record {
                    let stream_to_binding = stb.lock().await;
                    let binding = stream_to_binding
                        .get(&record.stream)
                        .ok_or(Error::DanglingConnectorRecord(record.stream))?;
                    let arena = record.data.get().as_bytes().to_vec();
                    let arena_len: u32 = arena.len() as u32;
                    resp.documents = Some(Documents {
                        binding: *binding as u32,
                        arena,
                        docs_json: vec![Slice {
                            begin: 0,
                            end: arena_len,
                        }],
                    });
                    drop(stream_to_binding);
                    Ok(Some((encode_message(&resp)?, (stb, stream))))
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

impl AirbyteSourceInterceptor {
    pub fn adapt_command_args(&mut self, op: &FlowCaptureOperation) -> Vec<String> {
        let config_file_path = self.input_file_path(CONFIG_FILE_NAME);
        let catalog_file_path = self.input_file_path(CATALOG_FILE_NAME);
        let state_file_path = self.input_file_path(STATE_FILE_NAME);

        let airbyte_args = match op {
            FlowCaptureOperation::Spec => vec!["spec"],
            FlowCaptureOperation::Discover => vec!["discover", "--config", &config_file_path],
            FlowCaptureOperation::Validate => vec!["check", "--config", &config_file_path],
            // TODO(johnny): These are effective no-ops, but as-written must invoke the connector.
            // We should refactor this.
            FlowCaptureOperation::ApplyUpsert | FlowCaptureOperation::ApplyDelete => vec!["spec"],
            FlowCaptureOperation::Pull => {
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
        op: &FlowCaptureOperation,
        in_stream: InterceptorStream,
    ) -> Result<InterceptorStream, Error> {
        let config_file_path = self.input_file_path(CONFIG_FILE_NAME);
        let catalog_file_path = self.input_file_path(CATALOG_FILE_NAME);
        let state_file_path = self.input_file_path(STATE_FILE_NAME);

        match op {
            FlowCaptureOperation::Spec => Ok(self.adapt_spec_request_stream(in_stream)),
            FlowCaptureOperation::Discover => {
                Ok(self.adapt_discover_request(config_file_path, in_stream))
            }
            FlowCaptureOperation::Validate => Ok(self.adapt_validate_request_stream(
                config_file_path,
                Arc::clone(&self.validate_request),
                in_stream,
            )),
            // TODO(johnny): These are effective no-ops, but as-written must invoke the connector.
            // We should refactor this.
            FlowCaptureOperation::ApplyUpsert | FlowCaptureOperation::ApplyDelete => {
                Ok(self.adapt_apply_request_stream(in_stream))
            }
            FlowCaptureOperation::Pull => Ok(self.adapt_pull_request_stream(
                config_file_path,
                catalog_file_path,
                state_file_path,
                Arc::clone(&self.stream_to_binding),
                in_stream,
            )),
        }
    }

    pub fn adapt_response_stream(
        &mut self,
        op: &FlowCaptureOperation,
        in_stream: InterceptorStream,
    ) -> Result<InterceptorStream, Error> {
        match op {
            FlowCaptureOperation::Spec => Ok(self.adapt_spec_response_stream(in_stream)),
            FlowCaptureOperation::Discover => Ok(self.adapt_discover_response_stream(in_stream)),
            FlowCaptureOperation::Validate => {
                Ok(self
                    .adapt_validate_response_stream(Arc::clone(&self.validate_request), in_stream))
            }
            FlowCaptureOperation::ApplyUpsert | FlowCaptureOperation::ApplyDelete => {
                Ok(self.adapt_apply_response_stream(in_stream))
            }
            FlowCaptureOperation::Pull => {
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
