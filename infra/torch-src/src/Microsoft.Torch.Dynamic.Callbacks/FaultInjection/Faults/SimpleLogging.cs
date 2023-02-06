// <copyright file="SimpleLogging.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Collections.Generic;
    using System.IO;

    /// <summary>
    /// Logs executed method signatures to a file.
    /// </summary>
    public class SimpleLogging : IFault
    {
        private string logFile;

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
            logFile = "Torch.log"; // default log file

            try
            {
                // first check if the faultParam is a directory name
                if (Directory.Exists(faultParam))
                {
                    logFile = Path.Combine(faultParam, "Torch.log");
                }
                else
                {
                    var dir = Path.GetDirectoryName(faultParam);
                    if (Directory.Exists(dir))
                    {
                        logFile = faultParam;
                    }
                }
            }
            catch
            {
            }
        }

        /// <inheritdoc/>
        public bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            exception = null;
            retValue = null;
            context = null;

            File.AppendAllLines(logFile, new List<string> { $"LOG: {methodSignature}" });
            return false;
        }

        /// <inheritdoc/>
        public object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            return retValue;
        }
    }
}
