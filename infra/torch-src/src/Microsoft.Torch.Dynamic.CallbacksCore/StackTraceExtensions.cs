namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Linq;
    using System.Reflection;
    using System.Runtime.CompilerServices;
    using System.Runtime.ExceptionServices;
    using System.Text;

    public static class StackTraceExtensions
    {
        public static List<StackFrameInfo> ToCleanStackTrace(this StackTrace stackTrace)
        {
            List<StackFrameInfo> cleanFrames = new List<StackFrameInfo>();

            if (stackTrace == null) throw new ArgumentNullException(nameof(stackTrace));
            var stackFrames = stackTrace.GetFrames();
            if (stackFrames == null) return null;

            var displayFilenames = true;

            var f = new StackFrame();


            foreach (var frame in stackFrames)
            {
                bool isAsync;
                string methodSignature;
                string fileName = null;
                int line = 0;

                var method = frame.GetMethod();

                if (method == null) continue;
                var declaringType = method.DeclaringType?.GetTypeInfo();
                // skip awaiters
                if (declaringType != null &&
                    (typeof(INotifyCompletion).GetTypeInfo().IsAssignableFrom(declaringType) ||
                     method.DeclaringType == typeof(ExceptionDispatchInfo)))
                {
                    continue;
                }

                var stringBuilder = new StringBuilder();
                isAsync = FormatMethodName(stringBuilder, declaringType);
                if (!isAsync)
                {
                    stringBuilder.Append(method.Name);
                    if (method is MethodInfo methodInfo && methodInfo.IsGenericMethod)
                    {
                        FormatGenericArguments(stringBuilder, methodInfo.GetGenericArguments());
                    }
                }
                else if (declaringType?.IsGenericType == true)
                {
                    // ReSharper disable once PossibleNullReferenceException
                    FormatGenericArguments(stringBuilder, declaringType.GenericTypeArguments);
                }
                stringBuilder.Append("(");
                if (isAsync)
                {
                    stringBuilder.Append("?");
                }
                else
                {
                    FormatParameters(stringBuilder, method);
                }
                stringBuilder.Append(")");

                methodSignature = stringBuilder.ToString();

                if (displayFilenames && frame.GetILOffset() != -1)
                {
                    try
                    {
                        fileName = frame.GetFileName();
                        line = frame.GetFileLineNumber();
                    }
                    catch
                    {
                        displayFilenames = false;
                    }
                }

                cleanFrames.Add(new StackFrameInfo(methodSignature, isAsync, fileName, line));
            }

            return cleanFrames;
        }

        public static string ToCleanString(this StackTrace stackTrace)
        {
            var frames = stackTrace.ToCleanStackTrace();
            return string.Join("\n", frames.Select(x => x.ToString()));
        }

        private static bool FormatMethodName(StringBuilder stringBuilder, TypeInfo declaringType)
        {
            if (declaringType == null) return false;
            var isAsync = false;
            var fullName = declaringType.FullName.Replace('+', '.');
            if (typeof(IAsyncStateMachine).GetTypeInfo().IsAssignableFrom(declaringType))
            {
                isAsync = true;
                var start = fullName.LastIndexOf('<');
                var end = fullName.LastIndexOf('>');
                if (start >= 0 && end >= 0)
                {
                    stringBuilder.Append(fullName.Remove(start, 1).Substring(0, end - 1));
                }
                else
                {
                    stringBuilder.Append(fullName);
                }
            }
            else
            {
                stringBuilder.Append(fullName);
                stringBuilder.Append(".");
            }
            return isAsync;
        }

        private static void FormatParameters(StringBuilder stringBuilder, MethodBase method)
        {
            var parameters = method.GetParameters();
            var firstParam = true;
            foreach (var t in parameters)
            {
                if (!firstParam)
                {
                    stringBuilder.Append(", ");
                }
                else
                {
                    firstParam = false;
                }
                // ReSharper disable once ConstantConditionalAccessQualifier
                // ReSharper disable once ConstantNullCoalescingCondition
                var typeName = t.ParameterType?.Name ?? "<UnknownType>";
                stringBuilder.Append(typeName + " " + t.Name);
            }
        }

        private static void FormatGenericArguments(StringBuilder stringBuilder, Type[] genericArguments)
        {
            stringBuilder.Append("[");
            var k = 0;
            var firstTypeParam = true;
            while (k < genericArguments.Length)
            {
                if (!firstTypeParam)
                {
                    stringBuilder.Append(",");
                }
                else
                {
                    firstTypeParam = false;
                }
                stringBuilder.Append(genericArguments[k].Name);
                k++;
            }
            stringBuilder.Append("]");
        }
    }
}
