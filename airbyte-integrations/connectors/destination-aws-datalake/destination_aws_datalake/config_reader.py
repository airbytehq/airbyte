class ConnectorConfig:
    def __init__(self,
                 AwsAccountId: str = None,
                 Region: str = None,
                 AuthMode:str= None,
                 AccessKeyId:str=None,
                 SecretAccessKey:str=None,
                 RoleArn:str=None,
                 BucketName: str = None,
                 Prefix: str = None,
                 DatabaseName: str = None,
                 TableName: str = None):
        self._aws = AwsAccountId
        self._auth = AuthMode
        self._access_key = AccessKeyId
        self._secret_key = SecretAccessKey
        self._role_arn= RoleArn
        self._region = Region
        self._bucket = BucketName
        self._prefix = Prefix
        self._database_name = DatabaseName
        self._table_name = TableName

    def __str__(self):
        return f"<S3Bucket(AwsAccountId={self.AwsAccountId},Region={self.Region},Bucket={self.BucketName},Auth={self.AuthMode}>"

    @property
    def AuthMode(self):
        return self._auth

    @property
    def AwsAccountId(self):
        return self._aws

    @property
    def Region(self):
        return self._region

    @property
    def BucketName(self):
        return self._bucket

    @property
    def Prefix(self):
        return self._prefix

    @property
    def AccessKeyId(self):
        return self._access_key

    @property
    def SecretAccessKey(self):
        return self._secret_key

    @property
    def RoleArn(self):
        return self._role_arn

    @property
    def DatabaseName(self):
        return self._database_name

    @property
    def TableName(self):
        return self._table_name

