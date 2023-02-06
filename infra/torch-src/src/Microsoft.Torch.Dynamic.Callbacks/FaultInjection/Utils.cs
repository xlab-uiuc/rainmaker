// <copyright file="Utils.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System.Text.RegularExpressions;

    /// <summary>
    /// Utility class.
    /// </summary>
    public class Utils
    {
        /// <summary>
        /// COnverts a wildcard to regex.
        /// </summary>
        /// <param name="wildcardText">wild card text.</param>
        /// <returns>a regex object.</returns>
        public static Regex WildCardToRegex(string wildcardText)
        {
            // var regexText = "^" + Regex.Escape(wildcardText).Replace("\\*", ".*").Replace("\\?", ".") + "$";
            var regexPattern = wildcardText
                .Replace(@"\", @"\\")
                .Replace(".", @"\.")
                .Replace("?", ".")
                .Replace("*", ".*?")
                .Replace(" ", @"\s");
            return new Regex(regexPattern, RegexOptions.IgnoreCase);
        }
    }
}
