use doc::ptr::Pointer;
use schemars::{schema::RootSchema, JsonSchema};

// Create the RootSchema given datatype T.
pub fn create_root_schema<T: JsonSchema>() -> RootSchema {
    let mut settings = schemars::gen::SchemaSettings::draft07();
    settings.inline_subschemas = true;
    let generator = schemars::gen::SchemaGenerator::new(settings);
    return generator.into_root_schema_for::<T>();
}

pub fn tokenize_jsonpointer(ptr: &str) -> Vec<String> {
    Pointer::from_str(&ptr)
        .iter()
        .map(ToString::to_string)
        .collect()
}

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_tokenize_jsonpointer() {
        let input = "/a/1/-/*";
        // It may be reasonable to instead have this function return an error or
        // panic if the pointer includes - or * tokens.
        let expected = [
            "a".to_string(),
            "1".to_string(),
            "-".to_string(),
            "*".to_string(),
        ];
        assert_eq!(&expected[..], &tokenize_jsonpointer(input));
    }
}
