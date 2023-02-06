package com.policies;

import org.mockserver.mock.action.ExpectationResponseCallback;
import org.mockserver.model.HttpRequest;
import org.mockserver.model.HttpResponse;
import org.mockserver.model.HttpStatusCode;

import static org.mockserver.model.Header.header;
import static org.mockserver.model.HttpResponse.response;

import java.util.UUID;

public class RequestBlockMockserver {
    public static class RequestBlockExpectationResponseCallback implements ExpectationResponseCallback {
        /**
         * Override the handler in the interface.
         * @param httpRequest
         * @return
         */
        @Override
        public HttpResponse handle(HttpRequest httpRequest) {
            String clientID = getRequestID(httpRequest);
            return craftResponse(httpRequest, clientID);
        }

        /**
         * Get the request ID by parsing the HTTP request header.
         * @param httpRequest
         * @return
         */
        public String getRequestID(HttpRequest httpRequest) {
            String clientRequestID;
            if (httpRequest.containsHeader("x-ms-client-request-id"))
                // Azure Storage
                clientRequestID = httpRequest.getHeader("x-ms-client-request-id").toString();
            else if (httpRequest.containsHeader("amz-sdk-invocation-id"))
                // AWS S3
                clientRequestID = httpRequest.getHeader("amz-sdk-invocation-id").toString();
            else if (httpRequest.containsHeader("X-Amz-Content-SHA256"))
                // AWS SQS
                clientRequestID = httpRequest.getHeader("X-Amz-Content-SHA256").toString();
            else if (httpRequest.containsHeader("x-ms-activity-id"))
                // Azure Cosmos
                clientRequestID = httpRequest.getHeader("x-ms-activity-id").toString();
            else
                clientRequestID = "UnknownRequestID";
            return clientRequestID;
        }

        /**
         * Craft the response with 503 Service Unavailable.
         * @param httpRequest
         * @param clientID
         * @return
         */
        public HttpResponse craftResponse(HttpRequest httpRequest, String clientID) {
            if (httpRequest.containsHeader("x-ms-client-request-id"))
                // Azure Storage
                return response()
                        .withStatusCode(HttpStatusCode.SERVICE_UNAVAILABLE_503.code())
                        .withHeaders(
                                header("x-ms-client-request-id", clientID.substring(1, clientID.length()-1)),
                                header("injected", "true")
                        );
            else if (httpRequest.containsHeader("amz-sdk-invocation-id"))
                // AWS S3
                return response()
                        .withStatusCode(HttpStatusCode.SERVICE_UNAVAILABLE_503.code())
                        .withHeaders(
                                header("amz-sdk-invocation-id", clientID.substring(1, clientID.length()-1)),
                                header("injected", "true")
                        );
            else if (httpRequest.containsHeader("X-Amz-Content-SHA256"))
                // AWS SQS
                return response()
                        .withStatusCode(HttpStatusCode.SERVICE_UNAVAILABLE_503.code())
                        .withHeaders(
                                header("X-Amz-Content-SHA256", clientID.substring(1, clientID.length()-1)),
                                header("injected", "true")
                        );
            else if (httpRequest.containsHeader("x-ms-activity-id"))
                // Azure Cosmos
                return response()
                        .withStatusCode(HttpStatusCode.SERVICE_UNAVAILABLE_503.code())
                        .withHeaders(
                                header("x-ms-activity-id", clientID.substring(1, clientID.length()-1)),
                                header("injected", "true")
                        );
            else
                return response()
                        .withStatusCode(HttpStatusCode.SERVICE_UNAVAILABLE_503.code())
                        .withHeaders(
                                header("injected", "true")
                        );
        }
    }
}
