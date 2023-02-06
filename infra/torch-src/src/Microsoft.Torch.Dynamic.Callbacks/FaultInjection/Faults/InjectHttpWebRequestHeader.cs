// <copyright file="InjectHttpWebRequestHeader.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Linq;
    using System.Net;
    using System.Net.Http;

#if FRAMEWORK
    using System.Runtime.Remoting.Messaging;
#endif

    /// <summary>
    /// Injects custom header into HttpWebRequests.
    /// </summary>
    public class InjectHttpWebRequestHeader : IFault
    {
        private static readonly string TorchHeaderName = "x-location";
        private static readonly string TorchContextName = "torch";

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
        }

        /// <inheritdoc/>
        public bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            exception = null;
            retValue = null;
            context = null;

            if (!methodSignature.StartsWith("System.Net"))
                return false;

            if (thisObj is HttpWebRequest)
            {
                var httpWebRequest = (HttpWebRequest)thisObj;

                var location = GetTorchContext();
                bool nonEmptyHeaderExists = httpWebRequest.Headers.AllKeys.Contains(TorchHeaderName) && !string.IsNullOrEmpty(httpWebRequest.Headers.Get(TorchHeaderName));
                if (!nonEmptyHeaderExists)
                {
                    // var stackTrace = Environment.StackTrace; // System.Diagnostics.EnhancedStackTrace.Current();
                    httpWebRequest.Headers.Add(TorchHeaderName, location?.ToString().Trim());
                }
            } else if (methodParams.Length > 0 && methodParams[0] is HttpRequestMessage)
            {
                var request = (HttpRequestMessage)methodParams[0];
                var location = GetTorchContext();
                bool nonEmptyHeaderExists = request.Headers.Contains(TorchHeaderName) && !string.IsNullOrEmpty(request.Headers.GetValues(TorchHeaderName).FirstOrDefault());

                if (!nonEmptyHeaderExists)
                {
                    request.Headers.Add(TorchHeaderName, location?.ToString().Trim());
                }
            }

            return false;
        }

        /// <inheritdoc/>
        public object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            return retValue;
        }

        private string GetTorchContext()
        {
            var context = CallContext.LogicalGetData(TorchContextName);
            if (context != null)
            {
                //var contextStack = (ImmutableStack<string>)context;
                //return string.Join("#", contextStack.ToList());
                return context.ToString();
            }

            return "null";
        }
    }
}
