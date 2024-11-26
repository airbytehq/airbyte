#define GIT_ATTR_CHECK_FILE_THEN_INDEX	0
#define GIT_ATTR_CHECK_INDEX_THEN_FILE	1
#define GIT_ATTR_CHECK_INDEX_ONLY		2
#define GIT_ATTR_CHECK_NO_SYSTEM        4
#define GIT_ATTR_CHECK_INCLUDE_HEAD     8
#define GIT_ATTR_CHECK_INCLUDE_COMMIT   16

#define GIT_ATTR_OPTIONS_VERSION ...

typedef enum {
	GIT_ATTR_VALUE_UNSPECIFIED = 0, /**< The attribute has been left unspecified */
	GIT_ATTR_VALUE_TRUE,   /**< The attribute has been set */
	GIT_ATTR_VALUE_FALSE,  /**< The attribute has been unset */
	GIT_ATTR_VALUE_STRING  /**< This attribute has a value */
} git_attr_value_t;

typedef struct {
	unsigned int version;
	unsigned int flags;
	git_oid *commit_id;
	git_oid attr_commit_id;
} git_attr_options;

int git_attr_get_ext(
	const char **value_out,
	git_repository *repo,
	git_attr_options *opts,
	const char *path,
	const char *name);

git_attr_value_t git_attr_value(const char *attr);
