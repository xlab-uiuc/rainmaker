package com.policies;

import org.mockserver.model.HttpRequest;
import org.mockserver.model.HttpResponse;

import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

import static com.Rainmaker.lock;
import static com.Rainmaker.sleepTime;
import static com.Rainmaker.injectionCNT;
import static com.Rainmaker.clientReqID;
import static com.Rainmaker.injectCallSiteStr;

public class TimeoutAll {
    public static class RequestForwardAndResponseCallback extends InjectionPolicy.RequestForwardAndResponseCallback {
        /**
         * Response handler function doing the fault injection on the response path.
         * It will inject faults for all the responses of a request with the unique call site
         * including retries in each test run.
         * @param httpRequest
         * @param httpResponse
         * @return
         * @throws InterruptedException
         */
        public HttpResponse handle(HttpRequest httpRequest, HttpResponse httpResponse) throws InterruptedException {
            String clientRequestID = getRequestID(httpRequest);
            boolean awsServiceFlag = checkAWSService(httpRequest);
            boolean idMatchFlag    = Objects.equals(clientReqID, clientRequestID);
            int statusCode         = httpResponse.getStatusCode();

            if ( (injectionCNT != 0 && !idMatchFlag) || (statusCode >= 300) )
                return httpResponse;

            HttpResponse retResponse;
            String xLocation = httpRequest.getHeader("x-Location").toString();
            String xLocationString = Objects.requireNonNull(Optional.ofNullable(xLocation)
                    .filter(str -> str.length() != 0)
                    .map(str -> str.substring(1, str.length() - 1))
                    .orElse(xLocation)).trim();

            String injectCallSiteString = injectCallSiteStr;
            //System.out.println("x-Location: "+xLocationString);
            //System.out.println("injectionString: "+injectCallSiteString);

            if (!injectCallSiteString.equals(xLocationString))
                return httpResponse;

            boolean isLockAcquired = lock.tryLock(sleepTime, TimeUnit.SECONDS);
            if (isLockAcquired) {
                try {
                    if (injectionCNT == 0)
                        clientReqID = clientRequestID;
                    injectionCNT += 1;
                    System.out.println("Injection happens!");
                    if (awsServiceFlag) {
                        TimeUnit.SECONDS.sleep(sleepTime);
                        return httpResponse.withHeader("injected", "true");
                    }
                    else {
                        retResponse = httpResponse.withStatusCode(408).withHeader("injected", "true");
                        retResponse = retResponse.withHeader("inject-cnt", String.valueOf(injectionCNT));
                        return retResponse;
                    }
                } finally {
                    lock.unlock();
                }
            }
            retResponse = httpResponse;
            return retResponse;
        }
    }
}

// In Ze stack trace: NullReferenceException <= only switch the HTTP status code 500
//                      We keep the body of the original response.
//                  =>  The original response body can let us know the corrupted state
//                          in the remote. => peek (retries multiple)
// In my stack trace: 503 RequestFailedException <= we manually craft a 503 resp

// //Inject 500 error code
// // Test the diff
// String uuidStr = UUID.randomUUID().toString();
// return response()
//     .withStatusCode(HttpStatusCode.INTERNAL_SERVER_ERROR_500.code())
//     .withHeaders(
//         header("x-ms-client-request-id", msClientReqID.substring(1, msClientReqID.length()-1)),
//         header("x-ms-request-id", uuidStr),
//         header("injected", "true")
//     );