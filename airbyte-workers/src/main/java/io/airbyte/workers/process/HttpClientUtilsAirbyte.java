package io.airbyte.workers.process;

import io.fabric8.kubernetes.api.model.ListOptions;
import io.fabric8.kubernetes.client.Config;
import io.fabric8.kubernetes.client.KubernetesClientException;
import io.fabric8.kubernetes.client.internal.SSLUtils;
import io.fabric8.kubernetes.client.utils.BackwardsCompatibilityInterceptor;
import io.fabric8.kubernetes.client.utils.ImpersonatorInterceptor;
import io.fabric8.kubernetes.client.utils.IpAddressMatcher;
import io.fabric8.kubernetes.client.utils.TokenRefreshInterceptor;
import io.fabric8.kubernetes.client.utils.Utils;
import okhttp3.ConnectionPool;
import okhttp3.ConnectionSpec;
import okhttp3.Credentials;
import okhttp3.Dispatcher;
import okhttp3.HttpUrl;
import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Protocol;
import okhttp3.Request;
import okhttp3.logging.HttpLoggingInterceptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.net.ssl.KeyManager;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import java.net.InetSocketAddress;
import java.net.MalformedURLException;
import java.net.Proxy;
import java.net.URL;
import java.security.GeneralSecurityException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.regex.PatternSyntaxException;

import static okhttp3.ConnectionSpec.CLEARTEXT;

public class HttpClientUtilsAirbyte {
    private HttpClientUtilsAirbyte() { }

    private static Pattern VALID_IPV4_PATTERN = null;
    public static final String ipv4Pattern = "(http:\\/\\/|https:\\/\\/)?(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.){3}([01]?\\d\\d?|2[0-4]\\d|25[0-5])(\\/[0-9]\\d|1[0-9]\\d|2[0-9]\\d|3[0-2]\\d)?";
    protected static final String KUBERNETES_BACKWARDS_COMPATIBILITY_INTERCEPTOR_DISABLE = "kubernetes.backwardsCompatibilityInterceptor.disable";

    static {
        try {
            VALID_IPV4_PATTERN = Pattern.compile(ipv4Pattern, Pattern.CASE_INSENSITIVE);
        } catch (PatternSyntaxException e) {
            throw KubernetesClientException.launderThrowable("Unable to compile ipv4address pattern.", e);
        }
    }

    public static OkHttpClient createHttpClient(final Config config) {
        return createHttpClient(config, (b) -> {});
    }

    public static OkHttpClient createHttpClientForMockServer(final Config config) {
        return createHttpClient(config, b -> b.protocols(Collections.singletonList(Protocol.HTTP_1_1)));
    }

    public static HttpUrl.Builder appendListOptionParams(HttpUrl.Builder urlBuilder, ListOptions listOptions) {
        if (listOptions == null) {
            return urlBuilder;
        }
        if (listOptions.getLimit() != null) {
            urlBuilder.addQueryParameter("limit", listOptions.getLimit().toString());
        }
        if (listOptions.getContinue() != null) {
            urlBuilder.addQueryParameter("continue", listOptions.getContinue());
        }

        if (listOptions.getResourceVersion() != null) {
            urlBuilder.addQueryParameter("resourceVersion", listOptions.getResourceVersion());
        }

        if (listOptions.getFieldSelector() != null) {
            urlBuilder.addQueryParameter("fieldSelector", listOptions.getFieldSelector());
        }

        if (listOptions.getLabelSelector() != null) {
            urlBuilder.addQueryParameter("labelSelector", listOptions.getLabelSelector());
        }

        if (listOptions.getTimeoutSeconds() != null) {
            urlBuilder.addQueryParameter("timeoutSeconds", listOptions.getTimeoutSeconds().toString());
        }

        if (listOptions.getAllowWatchBookmarks() != null) {
            urlBuilder.addQueryParameter("allowWatchBookmarks", listOptions.getAllowWatchBookmarks().toString());
        }

        if (listOptions.getWatch() != null) {
            urlBuilder.addQueryParameter("watch", listOptions.getWatch().toString());
        }
        return urlBuilder;
    }

    private static OkHttpClient createHttpClient(final Config config, final Consumer<OkHttpClient.Builder> additionalConfig) {
        try {
            OkHttpClient.Builder httpClientBuilder = new OkHttpClient.Builder();

            httpClientBuilder.connectionPool(new ConnectionPool(0, 30, TimeUnit.SECONDS));

            // Follow any redirects
            httpClientBuilder.followRedirects(true);
            httpClientBuilder.followSslRedirects(true);

            if (config.isTrustCerts() || config.isDisableHostnameVerification()) {
                httpClientBuilder.hostnameVerifier((s, sslSession) -> true);
            }

            TrustManager[] trustManagers = SSLUtils.trustManagers(config);
            KeyManager[] keyManagers = SSLUtils.keyManagers(config);

            if (keyManagers != null || trustManagers != null || config.isTrustCerts()) {
                X509TrustManager trustManager = null;
                if (trustManagers != null && trustManagers.length == 1) {
                    trustManager = (X509TrustManager) trustManagers[0];
                }

                try {
                    SSLContext sslContext = SSLUtils.sslContext(keyManagers, trustManagers);
                    httpClientBuilder.sslSocketFactory(sslContext.getSocketFactory(), trustManager);
                } catch (GeneralSecurityException e) {
                    throw new AssertionError(); // The system has no TLS. Just give up.
                }
            } else {
                SSLContext context = SSLContext.getInstance("TLSv1.2");
                context.init(keyManagers, trustManagers, null);
                httpClientBuilder.sslSocketFactory(context.getSocketFactory(), (X509TrustManager) trustManagers[0]);
            }

            List<Interceptor> interceptors = createApplicableInterceptors(config);
            interceptors.forEach(httpClientBuilder::addInterceptor);
            Logger reqLogger = LoggerFactory.getLogger(HttpLoggingInterceptor.class);
            if (reqLogger.isTraceEnabled()) {
                HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
                loggingInterceptor.setLevel(HttpLoggingInterceptor.Level.BODY);
                httpClientBuilder.addNetworkInterceptor(loggingInterceptor);
            }

            if (config.getConnectionTimeout() > 0) {
                httpClientBuilder.connectTimeout(config.getConnectionTimeout(), TimeUnit.MILLISECONDS);
            }

            if (config.getRequestTimeout() > 0) {
                httpClientBuilder.readTimeout(config.getRequestTimeout(), TimeUnit.MILLISECONDS);
            }

            if (config.getWebsocketPingInterval() > 0) {
                httpClientBuilder.pingInterval(config.getWebsocketPingInterval(), TimeUnit.MILLISECONDS);
            }

            if (config.getMaxConcurrentRequests() > 0 && config.getMaxConcurrentRequestsPerHost() > 0) {
                Dispatcher dispatcher = new Dispatcher();
                dispatcher.setMaxRequests(config.getMaxConcurrentRequests());
                dispatcher.setMaxRequestsPerHost(config.getMaxConcurrentRequestsPerHost());
                httpClientBuilder.dispatcher(dispatcher);
            }

            // Only check proxy if it's a full URL with protocol
            if (config.getMasterUrl().toLowerCase(Locale.ROOT).startsWith(Config.HTTP_PROTOCOL_PREFIX) || config.getMasterUrl().startsWith(Config.HTTPS_PROTOCOL_PREFIX)) {
                try {
                    URL proxyUrl = getProxyUrl(config);
                    if (proxyUrl != null) {
                        httpClientBuilder.proxy(new Proxy(Proxy.Type.HTTP, new InetSocketAddress(proxyUrl.getHost(), proxyUrl.getPort())));

                        if (config.getProxyUsername() != null) {
                            httpClientBuilder.proxyAuthenticator((route, response) -> {

                                String credential = Credentials.basic(config.getProxyUsername(), config.getProxyPassword());
                                return response.request().newBuilder().header("Proxy-Authorization", credential).build();
                            });
                        }
                    } else {
                        httpClientBuilder.proxy(Proxy.NO_PROXY);
                    }

                } catch (MalformedURLException e) {
                    throw new KubernetesClientException("Invalid proxy server configuration", e);
                }
            }

            if (config.getUserAgent() != null && !config.getUserAgent().isEmpty()) {
                httpClientBuilder.addNetworkInterceptor(chain -> {
                    Request agent = chain.request().newBuilder().header("User-Agent", config.getUserAgent()).build();
                    return chain.proceed(agent);
                });
            }

            if (config.getTlsVersions() != null && config.getTlsVersions().length > 0) {
                ConnectionSpec spec = new ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
                        .tlsVersions(config.getTlsVersions())
                        .build();
                httpClientBuilder.connectionSpecs(Arrays.asList(spec, CLEARTEXT));
            }

            if (shouldDisableHttp2() || config.isHttp2Disable()) {
                httpClientBuilder.protocols(Collections.singletonList(Protocol.HTTP_1_1));
            }

            if(additionalConfig != null) {
                additionalConfig.accept(httpClientBuilder);
            }

            if (config.getCustomHeaders() != null && !config.getCustomHeaders().isEmpty()) {
                httpClientBuilder.addNetworkInterceptor(chain -> {
                    Request.Builder agent = chain.request().newBuilder();
                    for (Map.Entry<String, String> entry : config.getCustomHeaders().entrySet()) {
                        agent.addHeader(entry.getKey(),entry.getValue());
                    }
                    return chain.proceed(agent.build());
                });
            }

            return httpClientBuilder.build();
        } catch (Exception e) {
            throw KubernetesClientException.launderThrowable(e);
        }
    }

    private static URL getProxyUrl(Config config) throws MalformedURLException {
        URL master = new URL(config.getMasterUrl());
        String host = master.getHost();
        if (config.getNoProxy() != null) {
            for (String noProxy : config.getNoProxy()) {
                if (isIpAddress(noProxy)) {
                    if (new IpAddressMatcher(noProxy).matches(host)) {
                        return null;
                    }
                } else {
                    if (host.contains(noProxy)) {
                        return null;
                    }
                }
            }
        }
        String proxy = config.getHttpsProxy();
        if (master.getProtocol().equals("http")) {
            proxy = config.getHttpProxy();
        }
        if (proxy != null) {
            return new URL(proxy);
        }
        return null;
    }

    private static boolean isIpAddress(String ipAddress) {
        Matcher ipMatcher = VALID_IPV4_PATTERN.matcher(ipAddress);
        return ipMatcher.matches();
    }

    /**
     * OkHttp wrongfully detects >JDK8u251 as which enables Http2
     * unsupported for JDK8.
     *
     * @return true if JDK8 is detected, false otherwise-
     * @see <a href="https://github.com/fabric8io/kubernetes-client/issues/2212">#2212</a>
     */
    private static boolean shouldDisableHttp2() {
        return System.getProperty("java.version", "").startsWith("1.8");
    }

    static List<Interceptor> createApplicableInterceptors(Config config) {
        List<Interceptor> interceptors = new ArrayList<>();
        // Header Interceptor
        interceptors.add(chain -> {
            Request request = chain.request();
            if (Utils.isNotNullOrEmpty(config.getUsername()) && Utils.isNotNullOrEmpty(config.getPassword())) {
                Request authReq = chain.request().newBuilder().addHeader("Authorization", Credentials.basic(config.getUsername(), config.getPassword())).build();
                return chain.proceed(authReq);
            } else if (Utils.isNotNullOrEmpty(config.getOauthToken())) {
                Request authReq = chain.request().newBuilder().addHeader("Authorization", "Bearer " + config.getOauthToken()).build();
                return chain.proceed(authReq);
            }
            return chain.proceed(request);
        });
        // Impersonator Interceptor
        interceptors.add(new ImpersonatorInterceptor(config));
        // Token Refresh Interceptor
        interceptors.add(new TokenRefreshInterceptor(config));
        // Backwards Compatibility Interceptor
        String shouldDisableBackwardsCompatibilityInterceptor = Utils.getSystemPropertyOrEnvVar(KUBERNETES_BACKWARDS_COMPATIBILITY_INTERCEPTOR_DISABLE, "false");
        if (!Boolean.parseBoolean(shouldDisableBackwardsCompatibilityInterceptor)) {
            interceptors.add(new BackwardsCompatibilityInterceptor());
        }

        return interceptors;
    }
}
