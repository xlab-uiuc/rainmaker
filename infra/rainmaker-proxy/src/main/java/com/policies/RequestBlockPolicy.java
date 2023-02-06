package com.policies;

import org.mockserver.mock.action.ExpectationForwardAndResponseCallback;
import org.mockserver.model.*;

import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

import static com.Rainmaker.*;
import static com.Rainmaker.lock;


public class RequestBlockPolicy {
    public static class RequestForwardAndResponseCallback extends InjectionPolicy.RequestForwardAndResponseCallback {
        /**
         * Request handler function that injects faults on the request path.
         * It will forward the request to another Mockserver which is able to return responses.
         * @param httpRequest
         * @return
         * @throws InterruptedException
         */
        public HttpRequest handle(HttpRequest httpRequest) throws InterruptedException {
            String xLocHeader      = httpRequest.getHeader("x-Location").toString();
            String xLocationString = Objects.requireNonNull(Optional.ofNullable(xLocHeader)
                    .filter(str -> str.length() != 0)
                    .map(str -> str.substring(1, str.length() - 1))
                    .orElse(xLocHeader)).trim();

            String injectCallSiteString = injectCallSiteStr;
            String requestHost          = httpRequest.getHeader("Host").toString();
            String clientRequestID      = getRequestID(httpRequest);
            boolean idMatched           = Objects.equals(clientReqID, clientRequestID);

            // TODO: is it possible to remove the callsite string compare? (redundant)
            if ((!injectCallSiteString.equals(xLocationString) || (injectionCNT != 0 && !idMatched))) {
                return dispatchRequest(requestHost, httpRequest);
            }

            boolean isLockAcquired = lock.tryLock(1, TimeUnit.SECONDS);
            if (isLockAcquired) {
                try {
                    if (injectionCNT == 0)
                        clientReqID = clientRequestID;
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
    }
}
