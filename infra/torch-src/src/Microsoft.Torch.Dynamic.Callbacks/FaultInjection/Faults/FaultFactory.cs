// <copyright file="FaultFactory.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;

    /// <summary>
    /// A fault factory.
    /// </summary>
    public class FaultFactory
    {
        /// <summary>
        /// Seperator of the parameters in the Init() parameter.
        /// </summary>
        public static readonly char[] FaultParamSep = ",".ToCharArray();

        /// <summary>
        /// Creates a fault.
        /// </summary>
        /// <param name="faultString">Fault string.</param>
        /// <returns>An IFault implementation.</returns>
        public static IFault CreateFault(string faultString)
        {
            try
            {
                string[] tokens = faultString.Split("()".ToCharArray(), StringSplitOptions.RemoveEmptyEntries);
                string faultName = tokens.Length > 0 ? tokens[0] : "Unknown";
                string faultValue = tokens.Length > 1 ? tokens[1] : null;

                var assembly = typeof(FaultFactory).Assembly;
                var obj = assembly.CreateInstance("Microsoft.Torch.Dynamic.FaultInjection." + faultName);
                if (obj == null || !(obj is IFault))
                {
                    return null;
                }

                var fault = obj as IFault;
                fault.Init(faultValue);
                return fault;
            }
            catch
            {
                return null;
            }
        }
    }
}
