// <copyright file="ThrowCosmosException.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Net;
    using System.Reflection;

    /// <summary>
    /// Create a CosmosDB exception.
    /// </summary>
    public class ThrowCosmosException : IFault
    {
        private Exception cosmosException;

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
            string[] tokens = faultParam.Split(",".ToCharArray());
            var httpStatusCode = Enum.Parse(typeof(HttpStatusCode), tokens[0]);
            var subStatusCode = tokens.Length > 1 ? int.Parse(tokens[1]) : 0;

            Type cosmosExceptionType = Type.GetType("Microsoft.Azure.Cosmos.CosmosException, Microsoft.Azure.Cosmos.Client");

            ConstructorInfo ctor = cosmosExceptionType?.GetConstructor(new[] { typeof(string), typeof(HttpStatusCode), typeof(int), typeof(string), typeof(double) });
            cosmosException = (Exception)ctor?.Invoke(new object[] { tokens[0], httpStatusCode, subStatusCode, null, 0 });
        }

        /// <inheritdoc/>
        public bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            retValue = null;
            context = null;
            exception = cosmosException ?? new Exception("CosmosException could not be created");
            return true;
        }

        /// <inheritdoc/>
        public object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            return retValue;
        }
    }
}
