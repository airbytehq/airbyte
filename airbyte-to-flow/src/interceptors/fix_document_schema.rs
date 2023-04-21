use doc::ptr::Token;
use serde_json::json;

use crate::errors::Error;
use serde_json::Map;


/// Given a document_schema_json and key ptrs, updates the document_schema to ensure that
/// the key pointers are always present in the document
pub fn fix_document_schema_keys(mut doc: serde_json::Value, key_ptrs: Vec<String>) -> Result<serde_json::Value, Error> {
    let original = doc.clone();
    for key in key_ptrs {
        let ptr = doc::Pointer::from_str(&key);

        let mut current = doc::Pointer::empty();
        for token in ptr.iter() {
            match token {
                // Add "minItems" to arrays to ensure the key is always available at that index
                doc::ptr::Token::Index(idx) => {
                    /* TODO: This code can have ambiguous results when encountering integer-like
                     * properties, and as such has been disabled for now.
                     * See https://github.com/estuary/airbyte/pull/46#discussion_r992250679
                     *
                    let parent = doc.pointer_mut(&current.to_string()).unwrap();
                    let min_items_required = idx as u64 + 1;
                    let parent_map = parent.as_object_mut().ok_or(Error::InvalidAirbyteSchema("expected array schema specification to be an object".to_string()))?;
                    parent_map.entry("minItems").and_modify(|e| {
                        if e.as_u64().unwrap_or(0) < min_items_required {
                            *e = json!(min_items_required)
                        }
                    }).or_insert(json!(min_items_required));

                    current.push(Token::Property("items"));*/
                    return Err(Error::InvalidAirbyteSchema(format!("cannot use JSONPointer index pointer /{}/ in key pointer at {}", idx, current)))
                },
                // Add "required" and ensure the property and its parent's type do not include null
                doc::ptr::Token::Property(prop) => {
                    let mut parent_map = doc.pointer_mut(&current.to_string())
                        .unwrap()
                        .as_object_mut()
                        .ok_or(Error::InvalidAirbyteSchema("expected object schema specification to be an object".to_string()))?;

                    // These advanced cases are not supported at the moment as we don't expect
                    // there to be many cases of them
                    if parent_map.contains_key("allOf") || parent_map.contains_key("anyOf") || parent_map.contains_key("not") {
                        tracing::debug!("automatic fixing of document schema keys for schemas with allOf, anyOf and not are not supported yet, skipping.");
                        return Ok(doc)
                    }

                    // If the object references a definition, use that definition
                    if parent_map.contains_key("$ref") {
                        let refr = parent_map.get("$ref").unwrap().as_str().unwrap().to_string();
                        parent_map = doc.pointer_mut("/$defs")
                            .and_then(|defs| defs.as_object_mut())
                            .and_then(|defs| defs.get_mut(&refr))
                            .and_then(|resolved_ref| resolved_ref.as_object_mut())
                            .ok_or(Error::InvalidAirbyteSchema(format!("expected to find $ref: {:?} in $defs", refr)))?;
                    }
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
                        .ok_or(Error::InvalidAirbyteSchema(format!("expected key {:?} to exist in 'properties' of \"{}\" in {}", prop, current, original)))?;

                    prop_schema.entry("type").and_modify(|e| {
                        if let Some(vec) = e.as_array_mut() {
                            if let Some(null_idx) = vec.iter().position(|item| item == "null") {
                                vec.swap_remove(null_idx);
                            }
                        }
                    });

                    current.push(Token::Property("properties".to_string()));
                    current.push(Token::Property(prop.to_string()));
                },
                doc::ptr::Token::NextIndex => return Err(Error::InvalidAirbyteSchema(format!("cannot use JSONPointer next index pointer /-/ in key pointer at {:?} in {:?}", current, original))),
            }
        }
    }

    Ok(doc)
}

pub fn traverse_jsonschema<F>(schema: &mut serde_json::Value, f: &mut F)
where F: FnMut(&mut Map<String, serde_json::Value>) -> () {
    match schema {
        serde_json::Value::Object(map) => {
            f(map);
            // keys under properties are schemas, so we need to run on those as well
            map.get_mut("properties").map(|props| {
                match props {
                    serde_json::Value::Object(inner_map) => {
                        inner_map.values_mut().for_each(|v| {
                            traverse_jsonschema(v, f);
                        });
                    },
                    _ => ()
                }
            });
            map.get_mut("items").map(|item| traverse_jsonschema(item, f));
        }
        _ => ()
    }
}

pub fn fix_nonstandard_jsonschema_attributes(schema: &mut serde_json::Value) {
    traverse_jsonschema(schema, &mut |map: &mut Map<String, serde_json::Value>| {
        // airbyte sometimes hides some fields from their config but keeps them
        // for backward compatibility
        map.remove("airbyte_hidden");

        // "group" is an attribute airbyte uses internally
        map.remove("group");

        // a mapping from a jsonschema type to an internal airbyte type
        map.remove("airbyte_type");

        // another attribute that is sometimes used in airbyte schemas
        map.remove("name");
    })
}

// enums are usually incomplete and new types are added to SaaS connectors over time which leads to enums breaking frequently
// they also do not usually have a specific materialization type, so we just remove them to avoid
// schema violations over time
pub fn remove_enums(schema: &mut serde_json::Value) {
    traverse_jsonschema(schema, &mut |map: &mut Map<String, serde_json::Value>| {
        map.remove("enum");
    })
}

#[cfg(test)]
mod test {
    use serde_json::json;

    use super::{fix_document_schema_keys, fix_nonstandard_jsonschema_attributes, remove_enums};

    #[test]
    fn test_fix_document_schema_keys_prop() {
        let doc_schema = r#"{
            "properties": {
                "id": {
                    "type": ["string", "null"]
                }
            }
        }"#.to_string();

        let key_ptrs = vec!["id".to_string()];

        assert_eq!(
            fix_document_schema_keys(serde_json::from_str(&doc_schema).unwrap(), key_ptrs).unwrap(),
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
    fn test_fix_document_schema_ref_and_defs() {
        let doc_schema = r#"{
            "$defs": {
                "test": {
                    "properties": {
                        "id": {
                            "type": ["string", "null"]
                        }
                    }
                }
            },
            "$ref": "test"
        }"#.to_string();

        let key_ptrs = vec!["id".to_string()];

        assert_eq!(
            fix_document_schema_keys(serde_json::from_str(&doc_schema).unwrap(), key_ptrs).unwrap(),
            json!({
                "$defs": {
                    "test": {
                        "properties": {
                            "id": {
                                "type": ["string"]
                            }
                        },
                        "required": ["id"]
                    }
                },
                "$ref": "test"
            })
        );
    }

    // We don't support this case yet, so the test just checks to make sure that we don't error out
    // either, just return the document as it was received
    #[test]
    #[allow(non_snake_case)]
    fn test_fix_document_schema_allOf() {
        let doc_schema = r#"{
            "$defs": {
                "test": {
                    "properties": {
                        "id": {
                            "type": ["string", "null"]
                        }
                    }
                }
            },
            "allOf": [{
                "$ref": "test"
            }, {
                "type": "object"
            }]
        }"#.to_string();

        let key_ptrs = vec!["id".to_string()];

        assert_eq!(
            fix_document_schema_keys(serde_json::from_str(&doc_schema).unwrap(), key_ptrs).unwrap(),
            json!({
                "$defs": {
                    "test": {
                        "properties": {
                            "id": {
                                "type": ["string", "null"]
                            }
                        }
                    }
                },
                "allOf": [{
                    "$ref": "test"
                }, {
                    "type": "object"
                }]
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

        let key_ptrs = vec!["0".to_string()];

        assert_eq!(
            fix_document_schema_keys(serde_json::from_str(&doc_schema).unwrap(), key_ptrs).unwrap(),
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

        let key_ptrs = vec!["doc/id".to_string()];

        assert_eq!(
            fix_document_schema_keys(serde_json::from_str(&doc_schema).unwrap(), key_ptrs).unwrap(),
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
    #[ignore]
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

        let key_ptrs = vec!["0/id".to_string()];

        assert_eq!(
            fix_document_schema_keys(serde_json::from_str(&doc_schema).unwrap(), key_ptrs).unwrap(),
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
    #[ignore]
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

        let key_ptrs = vec!["0/id".to_string()];

        assert_eq!(
            fix_document_schema_keys(serde_json::from_str(&doc_schema).unwrap(), key_ptrs).unwrap(),
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
    fn test_fix_nonstandard_jsonschema_attributes_multiple() {
        let doc_schema = r#"{
            "type": ["object", "null"],
            "airbyte_hidden": true,
            "properties": {
                "my_key": {
                    "type": ["object", "null"],
                    "properties": {
                        "group": {
                            "type": "array",
                            "items": {
                                "group": "x",
                                "type": "string"
                            }
                        },
                        "airbyte_type": {
                            "type": "string",
                            "airbyte_type": "string"
                        },
                        "id": {
                            "type": ["string", "null"],
                            "group": "test"
                        }
                    }
                }
            }
        }"#.to_string();

        let mut doc = serde_json::from_str(&doc_schema).unwrap();
        fix_nonstandard_jsonschema_attributes(&mut doc);
        assert_eq!(
            doc,
            json!({
                "type": ["object", "null"],
                "properties": {
                    "my_key": {
                        "type": ["object", "null"],
                        "properties": {
                            "group": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "airbyte_type": {
                                "type": "string"
                            },
                            "id": {
                                "type": ["string", "null"]
                            }
                        }
                    }
                }
            })
        );
    }

    #[test]
    #[allow(non_snake_case)]
    fn test_remove_enums() {
        let doc_schema = r#"{
            "type": ["object", "null"],
            "properties": {
                "my_key": {
                    "type": ["string"],
                    "enum": ["a", "b", "c"]
                }
            }
        }"#.to_string();

        let mut doc = serde_json::from_str(&doc_schema).unwrap();
        remove_enums(&mut doc);
        assert_eq!(
            doc,
            json!({
                "type": ["object", "null"],
                "properties": {
                    "my_key": {
                        "type": ["string"]
                    }
                }
            })
        );
    }
}
