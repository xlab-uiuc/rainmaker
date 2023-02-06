// <copyright file="ThrowSqlException.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Collections.Generic;
    using System.Data.SqlClient;
    using System.Linq;
    using System.Reflection;

    /// <summary>
    /// A fault that throws a SQL exception.
    /// </summary>
    public class ThrowSqlException : IFault
    {
        // SQL error codes: https://social.technet.microsoft.com/wiki/contents/articles/1541.windows-azure-sql-database-connection-management.aspx?Sort=MostUseful&PageIndex=2
        private static readonly int[] TransientErrorCodes = new int[] { 233, 4060, 40197, 40501, 40613, 49918, 49919, 49920, 11001 };
        private static readonly int[] BadStateErrorCodes = new int[] { 40544, 40549, 40550, 40551, 40552, 40553 };
        private static readonly int[] NetworkErrorCodes = new int[] { 40197, 40501, 40544, 40549, 40550, 40551, 40552, 40553, 40613 };
        private readonly Random random = new Random();
        private SqlException[] exceptions;

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
            // example params: "Transient", "BadState", "any", "default", "", "233,40549"
            faultParam = faultParam.Trim().ToLower();

            switch (faultParam)
            {
                case "transient":
                    exceptions = TransientErrorCodes.Select(x => NewSqlException(x)).ToArray();
                    break;
                case "badstate":
                    exceptions = BadStateErrorCodes.Select(x => NewSqlException(x)).ToArray();
                    break;
                case "network":
                    exceptions = NetworkErrorCodes.Select(x => NewSqlException(x)).ToArray();
                    break;
                case "any":
                case "random":
                case "default":
                case "":
                    var allErrorCodes = new int[TransientErrorCodes.Length + BadStateErrorCodes.Length];
                    TransientErrorCodes.CopyTo(allErrorCodes, 0);
                    BadStateErrorCodes.CopyTo(allErrorCodes, TransientErrorCodes.Length);
                    exceptions = allErrorCodes.Select(x => NewSqlException(x)).ToArray();
                    break;
                default:
                    var givenErrorCodes = ParseInts(faultParam);
                    exceptions = givenErrorCodes.Select(x => NewSqlException(x)).ToArray();
                    break;
            }
        }

        /// <inheritdoc/>
        public bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            retValue = null;
            context = null;
            exception = exceptions?.Length <= 0
                ? new Exception("No SqlException found to inject.")
                : exceptions[random.Next(exceptions.Length)];
            return true;
        }

        /// <inheritdoc/>
        public object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            return retValue;
        }

        private static int[] ParseInts(string commaSeparatedInts)
        {
            List<int> intList = new List<int>();
            string[] tokens = commaSeparatedInts.Split(",; ".ToCharArray(), StringSplitOptions.RemoveEmptyEntries);
            foreach (var t in tokens)
            {
                if (int.TryParse(t.Trim(), out int x))
                {
                    intList.Add(x);
                }
            }

            return intList.ToArray();
        }

        private static T Construct<T>(params object[] p)
        {
            var ctors = typeof(T).GetConstructors(BindingFlags.NonPublic | BindingFlags.Instance);
            return (T)ctors.First(ctor => ctor.GetParameters().Length == p.Length).Invoke(p);
        }

        private static SqlException NewSqlException(int number)
        {
            SqlErrorCollection collection = Construct<SqlErrorCollection>();

            SqlError error = Construct<SqlError>(number, (byte)2, (byte)3, "server name", "Error injected by Torch", "proc", 100);
            typeof(SqlErrorCollection)
                    .GetMethod("Add", BindingFlags.NonPublic | BindingFlags.Instance)
                    .Invoke(collection, new object[] { error });

            return typeof(SqlException)
                .GetMethod(
                    "CreateException",
                    BindingFlags.NonPublic | BindingFlags.Static,
                    null,
                    CallingConventions.ExplicitThis,
                    new[] { typeof(SqlErrorCollection), typeof(string) },
                    new ParameterModifier[] { })
                .Invoke(null, new object[] { collection, "7.0.0" }) as SqlException;
        }
    }
}
