// <copyright file="SlowDownSqlQuery.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Text.RegularExpressions;

    /// <summary>
    /// Injects delay into a sql query so that it runs slow on the server side.
    /// </summary>
    public class SlowDownSqlQuery : IFault
    {
        private double delaySeconds = 0;
        private Regex queryRegex;
        private bool debug;

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
            // example faultParam: "10.2,*,true"
            string[] tokens = faultParam.Split(FaultFactory.FaultParamSep);
            if (tokens.Length > 0)
            {
                delaySeconds = double.TryParse(tokens[0], out double d) ? d : 0;
            }

            if (tokens.Length > 1 && !string.IsNullOrWhiteSpace(tokens[1]))
            {
                queryRegex = Utils.WildCardToRegex(tokens[1]);
            }

            debug = tokens.Length > 2 && bool.TryParse(tokens[2], out bool b) && b;
        }

        /// <inheritdoc/>
        public bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            exception = null;
            retValue = null;
            context = null;
            if (methodSignature.Contains("set_CommandText"))
            {
                string queryString = methodParams[0]?.ToString();
                if (queryString != null
                    && queryString.StartsWith("SELECT ", StringComparison.OrdinalIgnoreCase))
                {
                    if (queryRegex == null || queryRegex.IsMatch(queryString))
                    {
                        string prefix = "WAITFOR DELAY '00:00:" + delaySeconds + "';";

                        if (debug)
                        {
                            Console.WriteLine($"DEBUG: slowing down query by {delaySeconds} seconds.");
                            Console.WriteLine($"DEBUG: Query: {prefix}{queryString}");
                        }

                        methodParams[0] = prefix + methodParams[0];
                    }
                }
            }

            return false;
        }

        /// <inheritdoc/>
        public object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            return retValue;
        }
    }
}
