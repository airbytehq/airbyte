use json::schema::formats::Format;
use json::validator::ValidationResult;
use regex::Regex;

use crate::errors::Error;

pub fn normalize_doc(
    doc: &mut serde_json::Value,
    _json_schema: &Option<serde_json::Value>,
) -> Result<(), Error> {
    // TODO: We should more intelligently use the schema to do normalization. I'm not going to take
    // the time to figure that out right now, so for now we are just handling the specific case in
    // https://github.com/estuary/airbyte/issues/123 with the field hs_latest_source_timestamp.
    normalize_datetime_to_date(doc, doc::Pointer::from_str("/hs_latest_source_timestamp"));

    Ok(())
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
                    "hs_latest_source_timestamp": "2023-03-05T15:41:54.565000+00:00"
                }),
                serde_json::json!({
                    "some": "thing",
                    "hs_latest_source_timestamp": "2023-03-05"
                }),
            ),
            (
                serde_json::json!({
                    "some": "thing",
                    "hs_latest_source_timestamp": "2023-03-05"
                }),
                serde_json::json!({
                    "some": "thing",
                    "hs_latest_source_timestamp": "2023-03-05" // Already a a date
                }),
            ),
            (
                serde_json::json!({
                    "some": "thing",
                    "hs_latest_source_timestamp": "hello",
                }),
                serde_json::json!({
                    "some": "thing",
                    "hs_latest_source_timestamp": "hello", // A string, but can't be normalized to a date
                }),
            ),
        ];

        for mut case in cases {
            normalize_doc(&mut case.0, &None).unwrap();
            assert_eq!(case.0, case.1);
        }
    }
}
