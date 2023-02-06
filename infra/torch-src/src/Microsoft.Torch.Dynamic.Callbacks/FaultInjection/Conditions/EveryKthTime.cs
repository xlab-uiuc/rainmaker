// <copyright file="EveryKthTime.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;

    /// <summary>
    /// A condition that is triggered ever k'th time.
    /// </summary>
    public class EveryKthTime : ICondition
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
            if (++invocationCount % k == 0)
            {
                invocationCount = 0;
                return true;
            }

            return false;
        }
    }
}
