#define GIT_FETCH_OPTIONS_VERSION ...
#define GIT_PUSH_OPTIONS_VERSION ...
#define GIT_REMOTE_CALLBACKS_VERSION ...

typedef enum {
	GIT_REMOTE_REDIRECT_NONE,
	GIT_REMOTE_REDIRECT_INITIAL,
	GIT_REMOTE_REDIRECT_ALL
} git_remote_redirect_t;

typedef enum git_remote_completion_t {
	GIT_REMOTE_COMPLETION_DOWNLOAD,
	GIT_REMOTE_COMPLETION_INDEXING,
	GIT_REMOTE_COMPLETION_ERROR,
} git_remote_completion_t;

typedef int (*git_push_transfer_progress_cb)(
	unsigned int current,
	unsigned int total,
	size_t bytes,
	void* payload);

typedef struct {
	char *src_refname;
	char *dst_refname;
	git_oid src;
	git_oid dst;
} git_push_update;

typedef int (*git_push_negotiation)(const git_push_update **updates, size_t len, void *payload);
typedef int (*git_push_update_reference_cb)(const char *refname, const char *status, void *data);
typedef int (*git_remote_ready_cb)(git_remote *remote, int direction, void *payload);
typedef int (*git_url_resolve_cb)(git_buf *url_resolved, const char *url, int direction, void *payload);

struct git_remote_callbacks {
	unsigned int version;
	git_transport_message_cb sideband_progress;
	int (*completion)(git_remote_completion_t type, void *data);
	git_credential_acquire_cb credentials;
	git_transport_certificate_check_cb certificate_check;
	git_indexer_progress_cb transfer_progress;
	int (*update_tips)(const char *refname, const git_oid *a, const git_oid *b, void *data);
	git_packbuilder_progress pack_progress;
	git_push_transfer_progress_cb push_transfer_progress;
	git_push_update_reference_cb push_update_reference;
	git_push_negotiation push_negotiation;
	git_transport_cb transport;
	git_remote_ready_cb remote_ready;
	void *payload;
	git_url_resolve_cb resolve_url;
};

typedef struct {
	unsigned int version;
	unsigned int pb_parallelism;
	git_remote_callbacks callbacks;
	git_proxy_options proxy_opts;
	git_remote_redirect_t follow_redirects;
	git_strarray custom_headers;
} git_push_options;

int git_push_options_init(
	git_push_options *opts,
	unsigned int version);

typedef enum {
	GIT_FETCH_PRUNE_UNSPECIFIED,
	GIT_FETCH_PRUNE,
	GIT_FETCH_NO_PRUNE,
} git_fetch_prune_t;

typedef enum {
	GIT_REMOTE_DOWNLOAD_TAGS_UNSPECIFIED = 0,
	GIT_REMOTE_DOWNLOAD_TAGS_AUTO,
	GIT_REMOTE_DOWNLOAD_TAGS_NONE,
	GIT_REMOTE_DOWNLOAD_TAGS_ALL,
} git_remote_autotag_option_t;

typedef struct {
	int version;
	git_remote_callbacks callbacks;
	git_fetch_prune_t prune;
	int update_fetchhead;
	git_remote_autotag_option_t download_tags;
	git_proxy_options proxy_opts;
	int depth;
	git_remote_redirect_t follow_redirects;
	git_strarray custom_headers;
} git_fetch_options;

int git_fetch_options_init(
	git_fetch_options *opts,
	unsigned int version);

int git_remote_list(git_strarray *out, git_repository *repo);
int git_remote_lookup(git_remote **out, git_repository *repo, const char *name);
int git_remote_create(
		git_remote **out,
		git_repository *repo,
		const char *name,
		const char *url);
int git_remote_create_with_fetchspec(
		git_remote **out,
		git_repository *repo,
		const char *name,
		const char *url,
		const char *fetch);
int git_remote_create_anonymous(
        git_remote **out,
        git_repository *repo,
        const char *url);
int git_remote_delete(git_repository *repo, const char *name);
const char * git_remote_name(const git_remote *remote);
int git_remote_rename(
	git_strarray *problems,
	git_repository *repo,
	const char *name,
	const char *new_name);
const char * git_remote_url(const git_remote *remote);
int git_remote_set_url(git_repository *repo, const char *remote, const char* url);
const char * git_remote_pushurl(const git_remote *remote);
int git_remote_set_pushurl(git_repository *repo, const char *remote, const char* url);
int git_remote_fetch(
		git_remote *remote,
		const git_strarray *refspecs,
		const git_fetch_options *opts,
		const char *reflog_message);
int git_remote_prune(git_remote *remote, const git_remote_callbacks *callbacks);
int git_remote_push(git_remote *remote,
				const git_strarray *refspecs,
				const git_push_options *opts);
const git_indexer_progress * git_remote_stats(git_remote *remote);
int git_remote_add_push(git_repository *repo, const char *remote, const char *refspec);
int git_remote_add_fetch(git_repository *repo, const char *remote, const char *refspec);
int git_remote_init_callbacks(
	git_remote_callbacks *opts,
	unsigned int version);
size_t git_remote_refspec_count(const git_remote *remote);
const git_refspec * git_remote_get_refspec(const git_remote *remote, size_t n);
int git_remote_get_fetch_refspecs(git_strarray *array, const git_remote *remote);
int git_remote_get_push_refspecs(git_strarray *array, const git_remote *remote);
void git_remote_free(git_remote *remote);

int git_remote_connect(
    git_remote *remote,
    int direction,
    const git_remote_callbacks *callbacks,
    const git_proxy_options *proxy_opts,
    const git_strarray *custom_headers);
int git_remote_ls(const git_remote_head ***out, size_t *size, git_remote *remote);
