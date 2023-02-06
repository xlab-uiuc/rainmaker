// <copyright file="FaultRule.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System.Text.RegularExpressions;

    /// <summary>
    /// The fault rule class.
    /// </summary>
    public class FaultRule
    {
        private readonly Regex target;
        private readonly ICondition condition;

        /// <summary>
        /// Initializes a new instance of the <see cref="FaultRule"/> class.
        /// </summary>
        /// <param name="targetPattern">The target method.</param>
        /// <param name="conditionString">The condition.</param>
        /// <param name="faultString">The fault.</param>
        public FaultRule(string targetPattern, string conditionString, string faultString)
        {
            if (targetPattern != null)
            {
                if (!targetPattern.Contains(";"))
                {
                    targetPattern = "*;" + targetPattern;
                }

                target = Utils.WildCardToRegex(targetPattern);
            }

            condition = ConditionFactory.CreateCondition(conditionString);
            Fault = FaultFactory.CreateFault(faultString);
        }

        /// <summary>
        /// Gets the fault object.
        /// </summary>
        public IFault Fault { get; }

        /// <summary>
        /// Determines if the fault rule is triggered.
        /// </summary>
        /// <param name="methodSignature">Method signature.</param>
        /// <returns>True if the rule is triggerred. False otherwise.</returns>
        public bool Triggered(string methodSignature) => target.IsMatch(methodSignature) && condition.Triggered();

        /// <summary>
        /// Determines if the fault rule is valid.
        /// </summary>
        /// <returns>True of the rule is valid.</returns>
        public bool IsValid() => target != null && Fault != null;
    }
}
