package com.policies;

import org.mockserver.mock.action.ExpectationForwardAndResponseCallback;
import org.mockserver.model.*;

import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

import static com.Rainmaker.lock;
import static com.Rainmaker.sleepTime;
import static com.Rainmaker.injectionCNT;
import static com.Rainmaker.injectCallSiteStr;

public class TimeoutSuccess {
    public static class RequestForwardAndResponseCallback extends InjectionPolicy.RequestForwardAndResponseCallback {
        /**
         * Response handler function doing the fault injection on the response path.
         * It will only inject once for one unique call site in each test run with considering the status code.
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
            int statusCode = httpResponse.getStatusCode();

            if (!injectCallSiteString.equals(xLocationString) || injectionCNT != 0 || (statusCode >= 300))
                return httpResponse;

            boolean isLockAcquired = lock.tryLock(sleepTime, TimeUnit.SECONDS);
            if (isLockAcquired) {
                try {
                    if (injectionCNT == 0) {
                        injectionCNT += 1;
                        System.out.println("Injection happens!!");
                        retResponse = httpResponse.withStatusCode(408).withHeader("injected", "true");
                        return retResponse;
                    }
                } finally{
                    lock.unlock();
                }
            }
            retResponse = httpResponse;
            return retResponse;
        }
    }
}

