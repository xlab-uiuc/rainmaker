package com.policies;

import org.mockserver.mock.action.ExpectationForwardAndResponseCallback;
import org.mockserver.model.*;

import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

import static com.Rainmaker.*;
import static org.mockserver.model.HttpOverrideForwardedRequest.forwardOverriddenRequest;
import static org.mockserver.model.HttpRequest.request;
import static org.mockserver.model.HttpResponse.response;
public class TimeoutBlindCosmos {
    public static class RequestForwardAndResponseCallback implements ExpectationForwardAndResponseCallback {
        @Override
        public HttpRequest handle(HttpRequest httpRequest) {
            return httpRequest;
        }

        @Override
        public HttpResponse handle(HttpRequest httpRequest, HttpResponse httpResponse) throws InterruptedException {
            HttpResponse retResponse;
            String xLocation = httpRequest.getHeader("x-Location").toString();
            String xLocationString = Objects.requireNonNull(Optional.ofNullable(xLocation)
                    .filter(str -> str.length() != 0)
                    .map(str -> str.substring(1, str.length() - 1))
                    .orElse(xLocation)).trim();

            // String injectCallSiteString = injectCallSiteStr;
            // String injectCallSiteString = "C:\\Users\\Ze\\CosmosDBStudio\\src\\CosmosDBStudio.Model\\Services\\Implementation\\DatabaseService.cs:68:Microsoft.Azure.Cosmos.Client;Microsoft.Azure.Cosmos.DatabaseInlineCore.DeleteAsync(Microsoft.Azure.Cosmos.RequestOptions,System.Threading.CancellationToken):CosmosDBStudio.Model.Services.Implementation.DatabaseService.DeleteDatabaseAsync(?)";
            String injectCallSiteString = "C:\\Users\\Ze\\CosmosDBStudio\\src\\CosmosDBStudio.Model\\Services\\Implementation\\ContainerService.cs:115:Microsoft.Azure.Cosmos.Client;Microsoft.Azure.Cosmos.ContainerInlineCore.DeleteContainerAsync(Microsoft.Azure.Cosmos.ContainerRequestOptions,System.Threading.CancellationToken):CosmosDBStudio.Model.Services.Implementation.ContainerService.DeleteContainerAsync(?)";
            // String injectCallSiteString = "C:\\Users\\Ze\\CosmosDBStudio\\src\\CosmosDBStudio.Model\\Services\\Implementation\\ContainerService.cs:26:Microsoft.Azure.Cosmos.Client;Microsoft.Azure.Cosmos.FeedIteratorInlineCore`1.ReadNextAsync(System.Threading.CancellationToken):CosmosDBStudio.Model.Services.Implementation.ContainerService.GetContainersAsync(?)";
            //            int statuscode = httpResponse.getStatusCode();
            //            System.out.println("x-Location: "+xLocationString);
            //            System.out.println("injectionString: "+injectCallSiteString);
            //            System.out.println(injectCallSiteString.equals(xLocationString));
            //            Optimization: directly return orig response if not the call site
            if (!injectCallSiteString.equals(xLocationString) || injectionCNT != 0)
                return httpResponse;
            //            The sequence of the request will be changed? e.g., retry will appear before the injected one

            boolean isLockAcquired = lock.tryLock(sleepTime, TimeUnit.SECONDS);
            if (isLockAcquired) {
                try {
                    if (injectionCNT == 0) {
                        injectionCNT += 1;
                        // Only inject once for one unique call site
                        System.out.println("injection happens!!");
                        // Inject Cosmos error codes - retriable error codes: 408, 410, 429, 449, 503
                        // https://docs.microsoft.com/en-us/azure/cosmos-db/sql/conceptual-resilient-sdk-applications#should-my-application-retry-on-errors
                        // retResponse = httpResponse.withStatusCode(cosmosErrorCode).withHeader("injected", "true");
                        // retResponse = httpResponse.withHeader("x-ms-substatus", "0");
                        // return retResponse;
                        //Inject real timeout - delay delivery of response:
                        retResponse = httpResponse.withHeader("injected", "true");
                        System.out.println("injection happens!!");
                        TimeUnit.SECONDS.sleep(sleepTime);
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
