use crate::errors::Error;

// Given a document, and a map of key -> value pointers,
// move the resident of "value" pointer to the "key" pointer, e.g.
// doc: { "title": "test" }, map: { "/name": "/title" } results in:
// { "name": "test" }
pub fn remap(doc: &mut serde_json::Value, mapping: &serde_json::Value) -> Result<(), Error> {
    let doc_copy = doc.clone();
    for (key, value) in mapping.as_object().unwrap() {
        let key_ptr = doc::Pointer::from_str(&key);
        let value_str = value.as_str().ok_or(Error::InvalidMapping(format!("expected {} key to have a string value", key)))?;
        let value_ptr = doc::Pointer::from_str(value_str);

        // copy from "value" pointer to "key" pointer
        {
            let location = key_ptr.create(doc).ok_or(Error::InvalidMapping(format!("could not query {} in document", key)))?;
            *location = value_ptr.query(&doc_copy).ok_or(Error::InvalidMapping(format!("could not query {} in document", value_str)))?.clone();
        }

        // remove what was at "value" pointer
        // TODO: replace this logic with a `value_ptr.pop()`
        // see https://github.com/estuary/flow/pull/768
        let (value_parent_str, child_key) = value_str.rsplit_once('/').ok_or(Error::InvalidMapping(format!("could not split {} to parent and child", value_str)))?;
        let value_parent_ptr = doc::Pointer::from_str(value_parent_str);
        let parent = value_parent_ptr.create(doc).ok_or(Error::InvalidMapping(format!("could not find {} in document", value_parent_str)))?;
        parent.as_object_mut().ok_or(Error::InvalidMapping(format!("expected {} to be an object", value_parent_str)))?.remove(child_key);
    }

    Ok(())
}

#[cfg(test)]
mod test {
    use serde_json::json;

    use super::remap;

    #[test]
    fn test_remap() {
        let mut doc = json!({
            "app_id": "id",
            "app_secret": "secret",
            "foo": "bar"
        });

        let map = json!({
            "/credentials/client_id": "/app_id",
            "/credentials/client_secret": "/app_secret"
        });

        remap(&mut doc, &map).unwrap();
        assert_eq!(
            doc,
            json!({
                "credentials": {
                    "client_id": "id",
                    "client_secret": "secret"
                },
                "foo": "bar"
            })
        );
    }
}
