package com.policies;

import org.mockserver.mock.action.ExpectationForwardAndResponseCallback;
import org.mockserver.model.HttpRequest;
import org.mockserver.model.HttpResponse;
import org.mockserver.model.SocketAddress;

public class InjectionPolicy {
    public static class RequestForwardAndResponseCallback implements ExpectationForwardAndResponseCallback {
        /**
         * Request handler function to proxy the HTTP traffic to the emulator or the real service.
         * @param httpRequest
         * @return
         */
        @Override
        public HttpRequest handle(HttpRequest httpRequest) throws InterruptedException {
           String requestHost = httpRequest.getHeader("Host").toString();
           //System.out.println(requestHost);
           return dispatchRequest(requestHost, httpRequest);
        }

        /**
         * Response handler function which only returns the response to the origin.
         * @param httpRequest
         * @param httpResponse
         * @return
         */
        @Override
        public HttpResponse handle(HttpRequest httpRequest, HttpResponse httpResponse) throws InterruptedException {
            return httpResponse;
        }

        /**
         * Dispatch the request according to its original destination.
         * @param host
         * @param httpRequest
         * @return
         */
        public HttpRequest dispatchRequest(String host, HttpRequest httpRequest) {
            switch (host) {
                case "[127.0.0.1:10000]":
                    httpRequest
                            .withSocketAddress("127.0.0.1", 20000, SocketAddress.Scheme.HTTPS);
                    break;
                case "[127.0.0.1:10001]":
                    httpRequest
                            .withSocketAddress("127.0.0.1", 20001, SocketAddress.Scheme.HTTPS);
                    break;
                case "[127.0.0.1:10002]":
                    httpRequest
                            .withSocketAddress("127.0.0.1", 20002, SocketAddress.Scheme.HTTPS);
                    break;
            }
            // For CosmosDB, it will use both localhost and 127.0.0.1,
            // so we choose to do the use the proxy all the traffic.
            return httpRequest;
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
         * Check whether the request is sent to an AWS service.
         * @param httpRequest
         * @return
         */
        public boolean checkAWSService(HttpRequest httpRequest) {
            if (httpRequest.containsHeader("x-ms-client-request-id"))
                // Azure Storage
                return false;
            else if (httpRequest.containsHeader("amz-sdk-invocation-id"))
                // AWS S3
                return true;
            else if (httpRequest.containsHeader("X-Amz-Content-SHA256"))
                // AWS SQS
                return true;
            else if (httpRequest.containsHeader("x-ms-activity-id"))
                // Azure Cosmos
                return false;
            else
                return false;
        }
    }
}
