// <copyright file="ICondition.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    /// <summary>
    /// ICondition interface.
    /// </summary>
    public interface ICondition
    {
        /// <summary>
        /// Initialize a conditon.
        /// </summary>
        /// <param name="parameter">Condition parameter.</param>
        void Init(string parameter);

        /// <summary>
        /// Determines if the condition is triggerred.
        /// </summary>
        /// <returns>True if the condition is triggered; false otherwise.</returns>
        bool Triggered();
    }
}
