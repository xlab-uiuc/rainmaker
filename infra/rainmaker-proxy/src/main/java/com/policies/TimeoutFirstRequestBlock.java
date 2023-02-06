package com.policies;

import org.mockserver.mock.action.ExpectationForwardAndResponseCallback;
import org.mockserver.model.HttpRequest;
import org.mockserver.model.HttpResponse;
import org.mockserver.model.SocketAddress;

import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

import static com.Rainmaker.*;

public class TimeoutFirstRequestBlock {
    public static class RequestForwardAndResponseCallback extends InjectionPolicy.RequestForwardAndResponseCallback {
        /**
         * Request handler function doing the fault injection for the first request.
         * @param httpRequest
         * @return
         * @throws InterruptedException
         */
        public HttpRequest handle(HttpRequest httpRequest) throws InterruptedException {
            String xLocHeader = httpRequest.getHeader("x-Location").toString();
            String xLocationString = Objects.requireNonNull(Optional.ofNullable(xLocHeader)
                    .filter(str -> str.length() != 0)
                    .map(str -> str.substring(1, str.length() - 1))
                    .orElse(xLocHeader)).trim();

            String injectCallSiteString = injectCallSiteStr;
            String requestHost          = httpRequest.getHeader("Host").toString();
            String clientRequestID      = getRequestID(httpRequest);
            boolean idMatchFlag         = Objects.equals(clientReqID, clientRequestID);

            if ((!injectCallSiteString.equals(xLocationString) || injectionCNT < 1 || !idMatchFlag))
                return dispatchRequest(requestHost, httpRequest);

            // TODO: Is one second is enough for the forwarding?
            boolean isLockAcquired = lock.tryLock(1, TimeUnit.SECONDS);
            if (isLockAcquired) {
                try {
                    injectionCNT += 1;
                    System.out.println("Injection happens!");
                    return httpRequest
                            .withSocketAddress("127.0.0.1", 30000, SocketAddress.Scheme.HTTPS);
                } finally {
                    lock.unlock();
                }
            }
            return dispatchRequest(requestHost, httpRequest);
        }

        /**
         * Response handler function doing the fault injection on the retry responses.
         * @param httpRequest
         * @param httpResponse
         * @return
         * @throws InterruptedException
         */
        public HttpResponse handle(HttpRequest httpRequest, HttpResponse httpResponse) throws InterruptedException {
            HttpResponse retResponse;
            String xLocation = httpRequest.getHeader("x-Location").toString();
            String xLocationString = Objects.requireNonNull(Optional.ofNullable(xLocation)
                    .filter(str -> str.length() != 0)
                    .map(str -> str.substring(1, str.length() - 1))
                    .orElse(xLocation)).trim();

            String injectCallSiteString = injectCallSiteStr;
            String clientRequestID      = getRequestID(httpRequest);
            boolean awsServiceFlag      = checkAWSService(httpRequest);

            if ((!injectCallSiteString.equals(xLocationString) || injectionCNT != 0))
                return httpResponse;

            boolean isLockAcquired = lock.tryLock(sleepTime, TimeUnit.SECONDS);
            if (isLockAcquired) {
                try {
                    clientReqID = clientRequestID;
                    injectionCNT += 1;
                    System.out.println("Injection happens!");
                    if (awsServiceFlag) {
                        TimeUnit.SECONDS.sleep(sleepTime);
                        retResponse = httpResponse.withHeader("injected", "true");
                    }
                    else {
                        retResponse = httpResponse.withStatusCode(408).withHeader("injected", "true");
                    }
                    retResponse = retResponse.withHeader("inject-cnt", String.valueOf(injectionCNT));
                    return retResponse;
                } finally {
                    lock.unlock();
                }
            }
            retResponse = httpResponse;
            return retResponse;
        }
    }
}
