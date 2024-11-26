#define GIT_PATH_MAX ...

typedef enum {
	GIT_FEATURE_THREADS	= (1 << 0),
	GIT_FEATURE_HTTPS	= (1 << 1),
	GIT_FEATURE_SSH		= (1 << 2),
	GIT_FEATURE_NSEC	= (1 << 3)
} git_feature_t;

int git_libgit2_features(void);
