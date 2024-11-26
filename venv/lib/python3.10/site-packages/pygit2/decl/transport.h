typedef struct git_credential git_credential;

typedef enum {
	GIT_CREDENTIAL_USERPASS_PLAINTEXT = (1u << 0),
	GIT_CREDENTIAL_SSH_KEY = (1u << 1),
	GIT_CREDENTIAL_SSH_CUSTOM = (1u << 2),
	GIT_CREDENTIAL_DEFAULT = (1u << 3),
	GIT_CREDENTIAL_SSH_INTERACTIVE = (1u << 4),
	GIT_CREDENTIAL_USERNAME = (1u << 5),
	GIT_CREDENTIAL_SSH_MEMORY = (1u << 6),
} git_credential_t;

typedef enum {
	GIT_CERT_SSH_MD5 = 1,
	GIT_CERT_SSH_SHA1 = 2,
} git_cert_ssh_t;

typedef struct {
	git_cert parent;
	git_cert_ssh_t type;
	unsigned char hash_md5[16];
	unsigned char hash_sha1[20];
} git_cert_hostkey;

typedef struct {
	git_cert parent;
	void *data;
	size_t len;
} git_cert_x509;

typedef int (*git_credential_acquire_cb)(
    git_credential **out,
    const char *url,
    const char *username_from_url,
    unsigned int allowed_types,
    void *payload);

typedef int (*git_transport_cb)(git_transport **out, git_remote *owner, void *param);
int git_credential_username_new(git_credential **out, const char *username);
int git_credential_userpass_plaintext_new(
	git_credential **out,
	const char *username,
	const char *password);

int git_credential_ssh_key_new(
	git_credential **out,
	const char *username,
	const char *publickey,
	const char *privatekey,
	const char *passphrase);

int git_credential_ssh_key_from_agent(
	git_credential **out,
	const char *username);

int git_credential_ssh_key_memory_new(
	git_credential **out,
	const char *username,
	const char *publickey,
	const char *privatekey,
	const char *passphrase);
