use doc::ptr::{Pointer, Token};
use schemars::{JsonSchema, schema::RootSchema};

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
        .map(|t| match t {
            // Keep the index and next index for now. Could adjust based on usecases.
            Token::Index(ind) => ind.to_string(),
            Token::Property(prop) => prop.to_string(),
            Token::NextIndex => "-".to_string(),
        })
        .collect()
}
