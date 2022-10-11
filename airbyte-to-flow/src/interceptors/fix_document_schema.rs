use doc::ptr::Token;
use serde_json::{value::RawValue, json};

use crate::errors::Error;


/// Given a document_schema_json and key ptrs, updates the document_schema to ensure that
/// the key pointers are always present in the document
pub fn fix_document_schema_keys(document_schema_json: &RawValue, key_ptrs: Vec<Vec<String>>) -> Result<serde_json::Value, Error> {
    let mut doc = serde_json::to_value(document_schema_json)?;
    for key in key_ptrs {
        let ptr = doc::Pointer::from_vec(&key);

        let mut current = doc::Pointer::empty();
        for token in ptr.iter() {
            match token {
                // Add "minItems" to arrays to ensure the key is always available at that index
                doc::ptr::Token::Index(idx) => {
                    let parent = doc.pointer_mut(&current.to_string()).unwrap();
                    let min_items_required = idx as u64 + 1;
                    let parent_map = parent.as_object_mut().ok_or(Error::InvalidAirbyteSchema("expected array schema specification to be an object".to_string()))?;
                    parent_map.entry("minItems").and_modify(|e| {
                        if e.as_u64().unwrap_or(0) < min_items_required {
                            *e = json!(min_items_required)
                        }
                    }).or_insert(json!(min_items_required));

                    current.push(Token::Property("items"));
                },
                // Add "required" and ensure the property and its parent's type do not include null
                doc::ptr::Token::Property(prop) => {
                    let parent = doc.pointer_mut(&current.to_string()).unwrap();
                    let parent_map = parent.as_object_mut().ok_or(Error::InvalidAirbyteSchema("expected object schema specification to be an object".to_string()))?;
                    let jprop = json!(prop);

                    parent_map.entry("required").and_modify(|e| {
                        let arr = e.as_array_mut().unwrap();
                        // If prop is not already required, mark it as required
                        if !arr.iter().any(|item| *item == jprop) {
                            arr.push(jprop);
                        }
                    }).or_insert(json!(vec![prop]));

                    parent_map.entry("type").and_modify(|e| {
                        if let Some(vec) = e.as_array_mut() {
                            // If the property's type includes "null", remove it
                            if let Some(null_idx) = vec.iter().position(|item| item == "null") {
                                vec.swap_remove(null_idx);
                            }
                        }
                    });

                    let prop_schema = parent_map
                        .get_mut("properties")
                        .and_then(|props| props.get_mut(prop))
                        .and_then(|schema| schema.as_object_mut())
                        .ok_or(Error::InvalidAirbyteSchema(format!("expected key {} to exist in 'properties' of {}", prop, current)))?;

                    prop_schema.entry("type").and_modify(|e| {
                        if let Some(vec) = e.as_array_mut() {
                            if let Some(null_idx) = vec.iter().position(|item| item == "null") {
                                vec.swap_remove(null_idx);
                            }
                        }
                    });

                    current.push(Token::Property("properties"));
                    current.push(Token::Property(prop));
                },
                doc::ptr::Token::NextIndex => return Err(Error::InvalidAirbyteSchema(format!("cannot use JSONPointer next index pointer /-/ in key pointer at {}", current))),
            }
        }
    }

    Ok(doc)
}

#[cfg(test)]
mod test {
    use serde_json::{json, value::RawValue};

    use super::fix_document_schema_keys;

    #[test]
    fn test_fix_document_schema_keys_prop() {
        let doc_schema = r#"{
            "properties": {
                "id": {
                    "type": ["string", "null"]
                }
            }
        }"#.to_string();

        let key_ptrs = vec![vec!["id".to_string()]];

        assert_eq!(
            fix_document_schema_keys(&RawValue::from_string(doc_schema).unwrap(), key_ptrs).unwrap(),
            json!({
                "properties": {
                    "id": {
                        "type": ["string"]
                    }
                },
                "required": ["id"]
            })
        );
    }

    #[test]
    #[ignore]
    fn test_fix_document_schema_keys_integer_prop() {
        let doc_schema = r#"{
            "properties": {
                "0": {
                    "type": ["string", "null"]
                }
            }
        }"#.to_string();

        let key_ptrs = vec![vec!["0".to_string()]];

        assert_eq!(
            fix_document_schema_keys(&RawValue::from_string(doc_schema).unwrap(), key_ptrs).unwrap(),
            json!({
                "properties": {
                    "0": {
                        "type": ["string"]
                    }
                },
                "required": ["0"]
            })
        );
    }

    #[test]
    fn test_fix_document_schema_keys_prop_deep() {
        let doc_schema = r#"{
            "properties": {
                "doc": {
                    "type": ["object", "null"],
                    "properties": {
                        "id": {
                            "type": ["string", "null"]
                        }
                    }
                }
            }
        }"#.to_string();

        let key_ptrs = vec![vec!["doc".to_string(), "id".to_string()]];

        assert_eq!(
            fix_document_schema_keys(&RawValue::from_string(doc_schema).unwrap(), key_ptrs).unwrap(),
            json!({
                "properties": {
                    "doc": {
                        "type": ["object"],
                        "properties": {
                            "id": {
                                "type": ["string"]
                            }
                        },
                        "required": ["id"]
                    }
                },
                "required": ["doc"]
            })
        );
    }

    #[test]
    fn test_fix_document_schema_keys_array() {
        let doc_schema = r#"{
            "items": {
                "type": ["object", "null"],
                "properties": {
                    "id": {
                        "type": ["string", "null"]
                    }
                }
            }
        }"#.to_string();

        let key_ptrs = vec![vec!["0".to_string(), "id".to_string()]];

        assert_eq!(
            fix_document_schema_keys(&RawValue::from_string(doc_schema).unwrap(), key_ptrs).unwrap(),
            json!({
                "minItems": 1,
                "items": {
                    "type": ["object"],
                    "properties": {
                        "id": {
                            "type": ["string"]
                        }
                    },
                    "required": ["id"]
                }
            })
        );
    }

    #[test]
    #[allow(non_snake_case)]
    fn test_fix_document_schema_keys_array_existing_minItems() {
        let doc_schema = r#"{
            "items": {
                "type": ["object", "null"],
                "properties": {
                    "id": {
                        "type": ["string", "null"]
                    }
                }
            },
            "minItems": 0
        }"#.to_string();

        let key_ptrs = vec![vec!["0".to_string(), "id".to_string()]];

        assert_eq!(
            fix_document_schema_keys(&RawValue::from_string(doc_schema).unwrap(), key_ptrs).unwrap(),
            json!({
                "minItems": 1,
                "items": {
                    "type": ["object"],
                    "properties": {
                        "id": {
                            "type": ["string"]
                        }
                    },
                    "required": ["id"]
                }
            })
        );
    }
}
