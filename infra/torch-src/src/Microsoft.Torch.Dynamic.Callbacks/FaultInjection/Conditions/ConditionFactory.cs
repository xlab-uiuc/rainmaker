// <copyright file="ConditionFactory.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;

    /// <summary>
    /// Condition factory.
    /// </summary>
    public class ConditionFactory
    {
        /// <summary>
        /// Creates a condition from a conditionString.
        /// </summary>
        /// <param name="conditionString">condition string.</param>
        /// <returns>A condition.</returns>
        public static ICondition CreateCondition(string conditionString)
        {
            string[] tokens = conditionString.Split("(,)".ToCharArray(), StringSplitOptions.RemoveEmptyEntries);
            string conditionName = tokens.Length > 0 ? tokens[0] : "Unknown";
            string conditionValue = tokens.Length > 1 ? tokens[1] : null;

            var assembly = typeof(ConditionFactory).Assembly;
            var obj = assembly.CreateInstance("Microsoft.Torch.Dynamic.FaultInjection." + conditionName);
            if (obj == null || !(obj is ICondition))
            {
                return new Never();
            }

            var condition = obj as ICondition;
            condition.Init(conditionValue);
            return condition;
        }
    }
}
