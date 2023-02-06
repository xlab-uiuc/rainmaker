// <copyright file="Always.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;

    /// <summary>
    /// A condition that always triggers.
    /// </summary>
    public class Always : ICondition
    {
        /// <inheritdoc/>
        public void Init(string parameter)
        {
        }

        /// <inheritdoc/>
        public bool Triggered() => true;
    }
}
