package io.airbyte.cdk.load.http.okhttp

import java.io.InputStream
import okhttp3.ResponseBody

class OkHttpResponseBody(private val responseBody: ResponseBody): InputStream() {

    override fun read(): Int {
        return responseBody.byteStream().read()
    }

    override fun close() {
        responseBody.close()
        super.close()
    }

}
