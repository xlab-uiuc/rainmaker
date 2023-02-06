// <copyright file="Never.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    /// <summary>
    /// A condition that is never triggered.
    /// </summary>
    public class Never : ICondition
    {
        /// <inheritdoc/>
        public void Init(string parameter)
        {
        }

        /// <inheritdoc/>
        public bool Triggered() => false;
    }
}
