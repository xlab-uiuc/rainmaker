// <copyright file="SlowDownSqlQueryClient.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Text.RegularExpressions;
    using System.Threading;

    /// <summary>
    /// Injects delay on the client side before making a sql query.
    /// </summary>
    public class SlowDownSqlQueryClient : IFault
    {
        private double delaySeconds = 0;
        private Regex queryRegex;
        private bool debug = false;

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
            // sample faultParam: "10,*,true"
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
            bool shouldInjectFault = methodSignature.Contains("ExecuteReader");
            if (shouldInjectFault)
            {
                if (debug)
                {
                    Console.WriteLine($"DEBUG: injecting delay for {delaySeconds} seconds.");
                }

                if (queryRegex != null)
                {
                    var queryString = thisObj.GetType().GetProperty("CommandText").GetValue(thisObj).ToString();
                    if (debug)
                    {
                        Console.WriteLine($"DEBUG: Query: {queryString}");
                    }

                    shouldInjectFault &= queryRegex.IsMatch(queryString);
                }
            }

            if (shouldInjectFault)
            {
                Thread.Sleep((int)(1000 * delaySeconds));
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
