use chrono::SecondsFormat;
use json::schema::formats::Format;
use json::validator::ValidationResult;
use regex::Regex;
use serde::Deserialize;
use crate::interceptors::fix_document_schema::traverse_jsonschema;
use serde_json::Map;
use dateparser::parse;

#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct NormalizationEntry {
    pub pointer: String,
    pub normalization: Normalization,
}

#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Normalization {
    DatetimeToDate,
}

pub fn normalize_doc(
    doc: &mut serde_json::Value,
    normalizations: &Option<Vec<NormalizationEntry>>
) {
    normalizations.as_ref().map(|entries| {
        for entry in entries {
            match entry.normalization {
                Normalization::DatetimeToDate => {
                    normalize_datetime_to_date(doc, doc::Pointer::from_str(&entry.pointer))
                }
            }
        }
    });
}

pub fn automatic_normalizations(
    doc: &mut serde_json::Value,
    schema: &mut serde_json::Value,
) {
    traverse_jsonschema(schema, &mut |map: &mut Map<String, serde_json::Value>, ptr: &str| {
        if map.get("format").and_then(|f| f.as_str()) == Some("date-time") {
            let pointer = doc::Pointer::from_str(ptr);
            normalize_to_rfc3339(doc, pointer);
        }
    }, "".to_string())
}

fn normalize_to_rfc3339(doc: &mut serde_json::Value, ptr: doc::Pointer) {
    if let Some(val) = ptr.query(doc) {
        val.to_owned().as_str().map(|v| {
            match Format::DateTime.validate(v) {
                ValidationResult::Valid => (), // Already a valid date
                _ => {
                    let parsed = parse(v).or_else(|_|
                        chrono::DateTime::parse_from_str(v, "%Y-%m-%dT%H:%M:%S%.3f%z").map(|d| d.with_timezone(&chrono::Utc))
                    );
                    if let Ok(parsed) = parsed {
                        let formatted = parsed.to_rfc3339_opts(SecondsFormat::AutoSi, true);
                            ptr.create_value(doc)
                            .map(|v| *v = serde_json::json!(formatted.as_str()));
                    }
                }
            };
        });
    }
}

lazy_static::lazy_static! {
    // This regex is very similar to DATE_RE in the Flow repo json crate, but will match anything
    // that looks like a date as long as it occurs at the beginning of the string.
    static ref EXTRACT_DATE_RE: Regex =
        Regex::new(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}").expect("Is a valid regex");
}

fn normalize_datetime_to_date(doc: &mut serde_json::Value, ptr: doc::Pointer) {
    if let Some(val) = ptr.query(doc) {
        val.to_owned().as_str().map(|v| {
            match Format::Date.validate(v) {
                ValidationResult::Valid => (), // Already a valid date
                _ => {
                    EXTRACT_DATE_RE.find(v).map(|mat| {
                        ptr.create_value(doc)
                            .map(|val| *val = serde_json::json!(mat.as_str()))
                    });
                }
            };
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn datetime_to_date() {
        let cases = vec![
            (
                serde_json::json!({
                    "some": "thing",
                    "properties": {
                        "hs_latest_source_timestamp": "2023-03-05T15:41:54.565000+00:00",
                    },
                }),
                serde_json::json!({
                    "some": "thing",
                    "properties": {
                        "hs_latest_source_timestamp": "2023-03-05",
                    },
                }),
            ),
            (
                serde_json::json!({
                    "some": "thing",
                    "properties": {
                        "hs_latest_source_timestamp": "2023-03-05",
                    },
                }),
                serde_json::json!({
                    "some": "thing",
                    "properties": {
                        "hs_latest_source_timestamp": "2023-03-05", // Already a a date
                    },
                }),
            ),
            (
                serde_json::json!({
                    "some": "thing",
                    "properties": {
                        "hs_latest_source_timestamp": "hello",
                    },
                }),
                serde_json::json!({
                    "some": "thing",
                    "properties": {
                        "hs_latest_source_timestamp": "hello", // A string, but can't be normalized to a date
                    },
                }),
            ),
        ];

        let normalizations = Some(vec![NormalizationEntry {
            pointer: "/properties/hs_latest_source_timestamp".to_string(),
            normalization: Normalization::DatetimeToDate,
        }]);

        for mut case in cases {
            normalize_doc(&mut case.0, &normalizations);
            assert_eq!(case.0, case.1);
        }
    }

    #[test]
    fn automatic_normalizations_rfc3339() {
        let cases = vec![
            (
                serde_json::json!({
                    "type": "object",
                    "properties": {
                        "created": {
                            "type": "string",
                            "format": "date-time"
                        },
                        "nested": {
                            "type": "object",
                            "properties": {
                                "x": {
                                    "type": ["string", "null"],
                                    "format": "date-time"
                                }
                            }
                        }
                    }
                }),
                serde_json::json!({
                    "created": "2023-01-30 02:34:15",
                    "nested": {
                        "x": "2020-03-25T21:03:18.000+0000"
                    }
                }),
                serde_json::json!({
                    "created": "2023-01-30T02:34:15Z",
                    "nested": {
                        "x": "2020-03-25T21:03:18Z"
                    }
                }),
            )
        ];

        for (mut schema, mut input, expected) in cases {
            automatic_normalizations(&mut input, &mut schema);
            assert_eq!(input, expected);
        }
    }
}
