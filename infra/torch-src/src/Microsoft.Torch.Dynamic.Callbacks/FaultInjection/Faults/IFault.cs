// <copyright file="IFault.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;

    /// <summary>
    /// IFault interface.
    /// </summary>
    public interface IFault
    {
        /// <summary>
        /// Initializes fault type.
        /// </summary>
        /// <param name="faultParam">a string with comma separated parameters.</param>
        void Init(string faultParam);

        /// <summary>
        /// Method invoked in the beginning of an instrumented method.
        /// </summary>
        /// <param name="thisObj">Instance object.</param>
        /// <param name="methodSignature">Method signature.</param>
        /// <param name="methodParams">An array of method parameters. Any changes to the parameters will be seen by the instrumented method.</param>
        /// <param name="exception">An exception to be thrown.</param>
        /// <param name="retValue">A value to be returned.</param>
        /// <param name="context">A context to be passed to OnEnd().</param>
        /// <returns>True if execution of the original method should be skipped. In that case, an exception is thrown if the exception is not null; otherwise the retValue is returned. Return false if the original method body should be executed.</returns>
        bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context);

        /// <summary>
        /// Method invoked at the end of an instrumented method.
        /// </summary>
        /// <param name="thisObj">Instance object.</param>
        /// <param name="methodSignature">Method signature.</param>
        /// <param name="methodParams">Method parameters.</param>
        /// <param name="retValue">Original return value.</param>
        /// <param name="contextFromOnStart">Context object from OnStart().</param>
        /// <returns>A value to be returned by the instrumented method.</returns>
        object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart);
    }
}
