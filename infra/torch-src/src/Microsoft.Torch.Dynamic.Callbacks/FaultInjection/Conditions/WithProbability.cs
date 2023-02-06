// <copyright file="WithProbability.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;

    /// <summary>
    /// A condition that is trigerred with a given probability.
    /// </summary>
    public class WithProbability : ICondition
    {
        private static readonly Random Random = new Random();
        private double probability = 0;

        /// <inheritdoc/>
        public void Init(string parameter)
        {
            probability = double.TryParse(parameter, out double p) ? p : 0;
        }

        /// <inheritdoc/>
        public bool Triggered() => Random.NextDouble() < probability;
    }
}
