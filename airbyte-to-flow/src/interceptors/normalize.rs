use crate::interceptors::fix_document_schema::traverse_jsonschema;
use dateparser::parse_with_timezone;
use chrono::{SecondsFormat, LocalResult, TimeZone};
use doc::ptr::Token;
use json::schema::formats::Format;
use json::validator::ValidationResult;
use regex::Regex;
use serde::Deserialize;
use serde_json::Map;

#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct NormalizationEntry {
    pub pointer: String,
    pub normalization: Normalization,
}

#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Normalization {
    DatetimeToDate
}

pub fn normalize_doc(
    doc: &mut serde_json::Value,
    normalizations: &Option<Vec<NormalizationEntry>>,
) {
    normalizations.as_ref().map(|entries| {
        for entry in entries {
            match entry.normalization {
                Normalization::DatetimeToDate => {
                    normalize_datetime_to_date(doc, &doc::Pointer::from_str(&entry.pointer))
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

            // traverse_jsonschema writes a /*/ pointer for array items. Here we check for such a star in the pointer
            // and expand it to normalize every item of the array. This implementation is kind of gross. Ideally we would have traverse_jsonschema
            // handle this more gracefully.
            let star_split = pointer.0.rsplit(|item| item == &Token::Property("*".to_string())).collect::<Vec<_>>();
            if star_split.len() > 1 {
                let property_in_item = &star_split[0][0];
                let array_parent = doc::Pointer(star_split[1].to_vec());

                array_parent.query(&doc.clone()).map(|val| {
                    val.as_array().map(|arr| {
                        for (i, _) in arr.iter().enumerate() {
                            let mut new_pointer = array_parent.clone();
                            new_pointer.push(Token::Index(i));
                            new_pointer.push(property_in_item.clone());
                            normalize_to_rfc3339(doc, &new_pointer);
                        }
                    })
                });
            } else {
                normalize_to_rfc3339(doc, &pointer);
            }
        }
    }, "".to_string())
}

// January 1st, 3000 is considered the maximum seconds unix timestamp
// It is January 12th, 1971 as a milliseconds unix timestamp
// This means we will not be able to support milliseconds unix timestamps before January 12th, 1971
// and we will not be able to support seconds unix timestamps after January 1st, 30000
const UNIX_SECONDS_MAX: i64 = 32503680000;

fn normalize_to_rfc3339(doc: &mut serde_json::Value, ptr: &doc::Pointer) {
    if let Some(val) = ptr.query(doc) {
        match val.to_owned() {
            serde_json::Value::String(val) => {
                match Format::DateTime.validate(&val) {
                    ValidationResult::Valid => (), // Already a valid date
                    _ => {
                        let parsed = parse_with_timezone(&val, &chrono::offset::Utc).or_else(|_|
                            chrono::DateTime::parse_from_str(&val, "%Y-%m-%dT%H:%M:%S%.3f%z").map(|d| d.with_timezone(&chrono::Utc))
                        ).or_else(|_|
                            chrono::DateTime::parse_from_str(&val, "%Y-%m-%dT%H:%M:%S%z").map(|d| d.with_timezone(&chrono::Utc))
                        ).or_else(|_|
                            chrono::NaiveDateTime::parse_from_str(&val, "%Y-%m-%dT%H:%M:%S%.3f").map(|d| d.and_local_timezone(chrono::Utc).unwrap())
                        );
                        if let Ok(parsed) = parsed {
                            let formatted = parsed.to_rfc3339_opts(SecondsFormat::AutoSi, true);
                                ptr.create_value(doc)
                                .map(|v| *v = serde_json::json!(formatted.as_str()));
                        }
                    }
                };    
            },
            serde_json::Value::Number(raw_num) => {
                let v = if raw_num.is_f64() {
                    (raw_num.as_f64().unwrap() * 1000_f64) as i64
                } else {
                    raw_num.as_i64().unwrap()
                };

                let (seconds_since_epoch, nanoseconds) = if v > UNIX_SECONDS_MAX {
                    let seconds = v / 1000;
                    let millis = (v % 1000) as u32;
                    (seconds, millis * 1000000)
                } else { (v, 0) };

                match chrono::Utc.timestamp_opt(seconds_since_epoch, nanoseconds) {
                    LocalResult::Single(dt) => {
                        let formatted = dt.to_rfc3339_opts(SecondsFormat::AutoSi, true);
                        ptr.create_value(doc)
                        .map(|val| *val = serde_json::json!(formatted.as_str()));
                    },
                    _ => {}
                };
            },
            _ => {}
        }
    }
}

lazy_static::lazy_static! {
    // This regex is very similar to DATE_RE in the Flow repo json crate, but will match anything
    // that looks like a date as long as it occurs at the beginning of the string.
    static ref EXTRACT_DATE_RE: Regex =
        Regex::new(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}").expect("Is a valid regex");
}

fn normalize_datetime_to_date(doc: &mut serde_json::Value, ptr: &doc::Pointer) {
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
            ),
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
                        "x": "2019-03-18T16:40:23+0000"
                    }
                }),
                serde_json::json!({
                    "created": "2023-01-30T02:34:15Z",
                    "nested": {
                        "x": "2019-03-18T16:40:23Z"
                    }
                }),
            ),
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
                        "x": "2021-03-02T23:00:00"
                    }
                }),
                serde_json::json!({
                    "created": "2023-01-30T02:34:15Z",
                    "nested": {
                        "x": "2021-03-02T23:00:00Z"
                    }
                }),
            ),
            (
                serde_json::json!({
                    "type": "object",
                    "properties": {
                        "seconds": {
                            "type": "string",
                            "format": "date-time"
                        },
                        "arr": {
                            "type": "array",
                            "items": {
                                "properties": {
                                    "milliseconds": {
                                        "type": "string",
                                        "format": "date-time"
                                    },
                                    "fractional_milliseconds": {
                                        "type": "string",
                                        "format": "date-time"
                                    }
                                }
                            }
                        }
                    }
                }),
                serde_json::json!({
                    "seconds": 1685098188,
                    "arr": [{
                        "milliseconds": 1685098188123_i64,
                        "fractional_milliseconds": 1685098188.123
                    }],
                }),
                serde_json::json!({
                    "seconds": "2023-05-26T10:49:48Z",
                    "arr": [{
                        "milliseconds": "2023-05-26T10:49:48.123Z",
                        "fractional_milliseconds": "2023-05-26T10:49:48.123Z"
                    }],
                }),
            )
        ];

        for (mut schema, mut input, expected) in cases {
            automatic_normalizations(&mut input, &mut schema);
            assert_eq!(input, expected);
        }
    }
}
