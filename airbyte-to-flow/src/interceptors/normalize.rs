use json::schema::formats::Format;
use json::validator::ValidationResult;
use regex::Regex;
use serde::Deserialize;

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
    normalizations: &Option<Vec<NormalizationEntry>>,
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
                        ptr.create(doc)
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
}
