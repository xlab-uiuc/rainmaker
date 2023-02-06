// <copyright file="HttpClientFault.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Net;
    using System.Net.Http;
    using System.Threading.Tasks;

    /// <summary>
    /// Faults for HttpClient.
    /// </summary>
    public class HttpClientFault : IFault
    {
        private HttpStatusCode statusCode;

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
            // faultParam should be a HttpStatusCode.
            if (!Enum.TryParse<HttpStatusCode>(faultParam, out statusCode))
            {
                statusCode = HttpStatusCode.ServiceUnavailable;
            }
        }

        /// <inheritdoc/>
        public bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            bool skipOriginal = true;
            retValue = null;
            context = null;
            exception = null;

            if (methodSignature.StartsWith("System.Net.Http;System.Net.Http.HttpClient.SendAsync"))
            {
                HttpResponseMessage response = new HttpResponseMessage();
                response.StatusCode = statusCode;

                retValue = Task.FromResult(response);
                skipOriginal = true;
            }
            else if (methodSignature.Contains("System.Net.HttpWebResponse.get_StatusCode"))
            {
                retValue = statusCode;
                skipOriginal = true;
            }

            return skipOriginal;
        }

        /// <inheritdoc/>
        public object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            return retValue;
        }
    }
}
