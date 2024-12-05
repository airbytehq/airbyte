# copy fb specs files from git
rm -rf facebook-business-sdk-codegen
git clone https://github.com/facebook/facebook-business-sdk-codegen

# prepare local directory structure
rm -rf schemas
mkdir schemas
mkdir schemas/shared

# generate fresh schemas
python schema_gen.py