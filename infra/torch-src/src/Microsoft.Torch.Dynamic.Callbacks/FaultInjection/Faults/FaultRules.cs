// <copyright file="FaultRules.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;
    using System.Text.RegularExpressions;
    using TinyJson;

    /// <summary>
    /// Fault rules.
    /// </summary>
    public class FaultRules
    {
        private readonly List<FaultRule> rules = new List<FaultRule>();

        /// <summary>
        /// Initializes a new instance of the <see cref="FaultRules"/> class.
        /// </summary>
        /// <param name="jsonConfigFile">json configuration file.</param>
        public FaultRules(string jsonConfigFile)
        {
            string jsonText = File.ReadAllText(jsonConfigFile);
            Dictionary<string, object> json = (Dictionary<string, object>)jsonText.FromJson<object>();
            var faultRules = (List<object>)json["faultRules"];
            foreach (var r in faultRules)
            {
                var rule = (Dictionary<string, object>)r;
                var target = rule.ContainsKey("target") ? rule["target"].ToString() : null;
                var when = rule.ContainsKey("when") ? rule["when"].ToString() : "Unknown";
                var fault = rule.ContainsKey("fault") ? rule["fault"].ToString() : null;

                if (target != null && fault != null)
                {
                    var tokens = target.Split("#".ToCharArray(), StringSplitOptions.None).Select(x => x.Trim());
                    foreach (var t in tokens)
                    {
                        var ruleObj = new FaultRule(t, when, fault);
                        if (ruleObj.IsValid())
                        {
                            rules.Add(ruleObj);
                        }
                    }
                }
            }

            Console.WriteLine($"{rules.Count} rules loaded!");
        }

        /// <summary>
        /// Finds the first triggered rule.
        /// </summary>
        /// <param name="methodSignature">method signature.</param>
        /// <returns>A triggered faultRule.</returns>
        public FaultRule TriggeredRule(string methodSignature)
        {
            return rules.Where(x => x.Triggered(methodSignature)).FirstOrDefault();
        }

        /// <summary>
        /// returns the number of active rules.
        /// </summary>
        /// <returns>the number of rules.</returns>
        public int RuleCount() => rules.Count;
    }
}
