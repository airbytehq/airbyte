import { apiOverride } from "core/request/apiOverride";

export interface RedirectUrlResponse {
  redirectUrl?: string;
}

// eslint-disable-next-line
type SecondParameter<T extends (...args: any) => any> = T extends (config: any, args: infer P) => any ? P : never;

/**
 * Return a JSON datastructure that contains the URL that should be redirected to in the redirectUrl field.
 * @summary Get the Speakeasy Callback URL
 */
export const getSpeakeasyCallbackUrl = (options?: SecondParameter<typeof apiOverride>, signal?: AbortSignal) => {
  return apiOverride<RedirectUrlResponse>({ url: `/speakeasy_callback_url`, method: "get", signal }, options);
};

type AwaitedInput<T> = PromiseLike<T> | T;

type Awaited<O> = O extends AwaitedInput<infer T> ? T : never;

export type GetSpeakeasyCallbackUrlResult = NonNullable<Awaited<ReturnType<typeof getSpeakeasyCallbackUrl>>>;
