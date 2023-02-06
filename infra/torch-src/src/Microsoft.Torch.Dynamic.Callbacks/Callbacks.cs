// <copyright file="Callbacks.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using Microsoft.Torch.Dynamic.FaultInjection;

    /// <summary>
    /// Implements the callbacks called by instrumented methods
    /// Important: Do not change callback signatures; they are hard coded in instrumented code.
    /// </summary>
    public class Callbacks
    {
        private static readonly FaultRules FaultRules;
        private static readonly string LogFilePath;

        static Callbacks()
        {
            bool isFramework = typeof(object).Assembly.GetName().Name == "mscorlib";
            string profilerHome = isFramework ? Environment.GetEnvironmentVariable("TORCH_CALLBACK_HOME") : Environment.GetEnvironmentVariable("TORCHCORE_CALLBACK_HOME");
            string faultConfigFilePath = Path.Combine(profilerHome, "TorchConfig.json");
            FaultRules = new FaultRules(faultConfigFilePath);

            LogFilePath = Path.Combine(profilerHome, "torch" + System.Diagnostics.Process.GetCurrentProcess().Id+ ".log");
        }

        /// <summary>
        /// Callback called in the beginning of an instrumented method.
        /// </summary>
        /// <param name="thisObj">Object of the caller method.</param>
        /// <param name="methodSignature">Name of the method.</param>
        /// <param name="methodParams">An array with all parameters.</param>
        /// <param name="exception">An exception to throw. If the value is not null, the method will throw an exception and return, without executing the original code or OnEnd callback.</param>
        /// <param name="retValue">Return value in case the original method is skipped.</param>
        /// <param name="context">An object that is passed to OnEnd.</param>
        /// <returns>True, if the method should return without executing the original method body; false otherwise.
        /// If True, the instrumented method throws an exception (if exception is not null)
        /// or returns the "context" as returnValue of the method (if exception is null).
        /// If False, execution of the original method continues, and the "context" is provided to the OnEnd() callback.
        /// </returns>
        public static bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            exception = null;
            retValue = null;

            var faultRule = FaultRules.TriggeredRule(methodSignature);
            var callbackContext = new FaultCallbackContext();
            callbackContext.FaultRule = faultRule;

            // var logLine = $"[{DateTime.Now}] [OnBegin] {methodSignature}";
            // File.AppendAllLines(LogFilePath, new List<string>() { logLine });
            object onBeginState = null;
            var skipOriginal = faultRule?.Fault.OnBegin(thisObj, methodSignature, methodParams, out exception, out retValue, out onBeginState);
            callbackContext.State = onBeginState;

            context = callbackContext;

            return skipOriginal.HasValue ? skipOriginal.Value : false;
        }

        /// <summary>
        /// Callback called at the end of an instrumented method.
        /// </summary>
        /// <param name="thisObj">instance object.</param>
        /// <param name="methodSignature">Method name.</param>
        /// <param name="methodParams">An array with all parameters.</param>
        /// <param name="retValue">Return value of the uninstrumented method. Null if the method does not return anything.</param>
        /// <param name="contextFromOnStart">Context object returned by the OnStart() callback.</param>
        /// <returns>An object that is finally returned by the instrumented method.</returns>
        public static object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            var faultContext = (FaultCallbackContext)contextFromOnStart;
            if (faultContext.FaultRule != null)
            {
                return faultContext.FaultRule.Fault.OnEnd(thisObj, methodSignature, methodParams, retValue, faultContext.State);
            }

            return retValue;
        }

        private static void PrintParams(object[] args)
        {
            if (args.Length > 0 && args[0] != null && args[0].ToString().StartsWith("Select", StringComparison.OrdinalIgnoreCase))
            {
                foreach (var o in args)
                {
                    Console.Write(o + " ");
                }

                Console.WriteLine();
            }
        }
    }
}
