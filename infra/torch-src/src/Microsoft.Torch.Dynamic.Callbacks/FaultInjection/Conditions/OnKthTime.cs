// <copyright file="OnKthTime.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;

    /// <summary>
    /// A condition that is triggered on kth time.
    /// </summary>
    public class OnKthTime : ICondition
    {
        private int k;
        private int invocationCount = 0;

        /// <inheritdoc/>
        public void Init(string parameter)
        {
            k = int.TryParse(parameter, out int i) ? i : 0;
        }

        /// <inheritdoc/>
        public bool Triggered()
        {
            if (invocationCount < k)
            {
                invocationCount++;
            }

            return invocationCount == k;
        }
    }
}
