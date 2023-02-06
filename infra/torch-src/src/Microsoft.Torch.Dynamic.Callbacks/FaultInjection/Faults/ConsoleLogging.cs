// <copyright file="ConsoleLogging.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;

    /// <summary>
    /// Prints a given message to console at the beginning of each instrumented method. Used for debugging purpose only.
    /// </summary>
    public class ConsoleLogging : IFault
    {
        private string message;

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
            message = faultParam;
        }

        /// <inheritdoc/>
        public bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            exception = null;
            retValue = null;
            context = null;
            Console.WriteLine($"{methodSignature} : {message}");
            return false;
        }

        /// <inheritdoc/>
        public object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            return retValue;
        }
    }
}
