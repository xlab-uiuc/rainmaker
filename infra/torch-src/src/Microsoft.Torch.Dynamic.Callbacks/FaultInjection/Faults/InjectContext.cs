// <copyright file="InjectContext.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Diagnostics;
    using System.Linq;
    using System.Reflection;
    using System.Threading.Tasks;

#if FRAMEWORK
    using System.Runtime.Remoting.Messaging;
#endif

    /// <summary>
    /// Injects context into call context.
    /// </summary>
    public class InjectContext : IFault
    {
        private static readonly string TorchContextKey = "torch";
        private static bool firstFr = true;

        /// <inheritdoc/>
        public void Init(string faultParam)
        {
        }

        /// <inheritdoc/>
        public bool OnBegin(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        {
            bool skipOriginal = false;

            exception = null;
            retValue = null;
            context = false;

            //// keep track of the chain of Azure SDK API calls
            //if (CallContext.LogicalGetData(TorchContextKey) == null)
            //{
            //    CallContext.LogicalSetData(TorchContextKey, ImmutableStack<string>.Empty);
            //}

            //if (CallContext.LogicalGetData(TorchContextKey) == null)
            //{
            //    CallContext.LogicalSetData(TorchContextKey, "");
            //}

            string location = null;

#if FRAMEWORK
            var topFrame = EnhancedStackTrace.Current().GetFrames().Where(x => !FrameShouldBeIgnored(x)).FirstOrDefault();
            if (topFrame != null)
            {
                location = $"{topFrame.GetFileName()}:{topFrame.GetFileLineNumber()}:{methodSignature}:{topFrame.GetMethod()}";
            }
            //if (topFrame != null && firstFr) 
            //{
            //    location = $"{topFrame.GetFileName()}:{topFrame.GetFileLineNumber()}:{methodSignature}:{topFrame.ToString()}";
            //    firstFr = false;
            //}
            //else if (topFrame != null)
            //{
            //    location = $"{topFrame.GetFileName()}:{topFrame.GetFileLineNumber()}:{methodSignature}";
            //}
#else
            var topFrame = new StackTrace(true).ToCleanStackTrace()?.Where(x => !FrameShouldBeIgnored(x)).FirstOrDefault();
            if (topFrame != null)
            {
                location = $"{topFrame.FileName}:{topFrame.Line}:{methodSignature}:{topFrame.Method}";
            }
            //if (topFrame != null && firstFr)
            //{
            //    location = $"{topFrame.FileName}:{topFrame.Line}:{methodSignature}:{topFrame.ToString()}";
            //    firstFr = false;
            //}
            //else if (topFrame != null)
            //{
            //    location = $"{topFrame.FileName}:{topFrame.Line}:{methodSignature}";
            //}
#endif
            // Yf: For tracing internal SDK API call chains
            //if (location != null)
            //{
            //    var contextStack = (ImmutableStack<string>)CallContext.LogicalGetData(TorchContextKey);
            //    contextStack = contextStack.Push(location);
            //    CallContext.LogicalSetData(TorchContextKey, contextStack);
            //    context = true; // true means call context was set by this method call
            //}

            // only track the first Azure SDK API call
            var torchContext = CallContext.LogicalGetData(TorchContextKey);
            if (torchContext != null)
            {
                // we only remember the first method call in the call stack
                return skipOriginal;
            }

            //var topFrame = EnhancedStackTrace.Current().GetFrames().Where(x => !FrameShouldBeIgnored(x)).FirstOrDefault();

            if (location != null)
            {
                // var location = $"{topFrame.GetFileName()}:{topFrame.GetFileLineNumber()}:{methodSignature}:{topFrame.ToString()}";
                CallContext.LogicalSetData(TorchContextKey, location);
                context = true; // true means call context was set by this method call
            }

            return skipOriginal;
        }

        private bool FrameContainingMethodName(StackFrame frame, string targetMethodName)
        {
            var frameMethodFullName = frame.GetMethod().DeclaringType.FullName + "." + frame.GetMethod().Name;
            return (frameMethodFullName.Contains(targetMethodName));
        }

#if FRAMEWORK
        private bool FrameShouldBeIgnored(StackFrame frame)
        {
            if (string.IsNullOrEmpty(frame.GetFileName())) return true;

            var typeName = frame.GetMethod().DeclaringType.FullName;
            if (typeName.Contains("Microsoft.Torch")) return true;

            return false;
        }
#else
        private bool FrameShouldBeIgnored(StackFrameInfo frame)
        {
            if (string.IsNullOrEmpty(frame.FileName)) return true;

            if (frame.Method.Contains("Microsoft.Torch")) return true;

            return false;
        }
#endif
        /// <inheritdoc/>
        public object OnEnd(object thisObj, string methodSignature, object[] methodParams, object retValue, object contextFromOnStart)
        {
            if (retValue != null && retValue is Task)
            {
                var task = (Task)retValue;
                try
                {
                    task.Wait(); // force the async task to finish before we clear up the call context 
                }
                catch
                {
                }
            }

            // clear call context when a method finishes
            var contextSetByThisMethod = (bool)contextFromOnStart;
            if (contextSetByThisMethod)
            {
                // Yf: use stack to trace internal SDK API call chain
                //var contextStack = (ImmutableStack<string>)CallContext.LogicalGetData(TorchContextKey);
                //CallContext.LogicalSetData(TorchContextKey, contextStack.Pop());

                // Yf: only trace the public entry API
                CallContext.LogicalSetData(TorchContextKey, null);
            }

            return retValue;
        }

        private bool IsCompilerGenerated(MethodBase method)
        {
            return method.DeclaringType.Name.Contains("<");
        }

        /// <inheritdoc/>
        //public bool OnBeginOld(object thisObj, string methodSignature, object[] methodParams, out Exception exception, out object retValue, out object context)
        //{
        //    exception = null;
        //    retValue = null;
        //    context = null;

        //    var knownLocation = CallContext.LogicalGetData("torch");
        //    var knownLocationString = knownLocation == null ? string.Empty : knownLocation.ToString().Trim();

        //    //var stackTrace = Environment.StackTrace;
        //    //var location = stackTrace.ToString();


        //   //var firstFrame = new StackTrace(true).GetFrames().Where(x => x.GetFileName() != null && !IsCompilerGenerated(x.GetMethod())).FirstOrDefault();
        //    ////var methodName = firstFrame.GetMethod().Name;
        //    //var location = firstFrame?.ToString().Trim();

        //    //var frames = new StackTrace(true).GetFrames().Where(x => x.GetFileName() != null && !IsCompilerGenerated(x.GetMethod())).Select(x => x.ToString().Trim()).ToList();

        //    //var frames = new StackTrace(true).GetFrames().ToList();//.Where(x => x.GetFileName() != null).Select(x => x.ToString().Trim()).ToList();
        //    //var frameString = string.Join(";", frames);

        //    //var location = frameString;


        //    string prevMethodName = String.Empty;
        //    StackFrame prevStackFrame = null;

        //    var frames = new StackTrace(true).GetFrames().ToList();
        //    //Select(x => x.ToString().Trim())
        //    var location = String.Empty;
        //    foreach (StackFrame fr in frames)
        //    {
        //        if (fr.GetFileName() != null)
        //        {
        //            if (!fr.GetMethod().DeclaringType.Name.Contains("<"))
        //            {
        //                //constructor function in Azure SDK
        //                location = fr.GetMethod().Name + " at " + fr.GetFileName() + ":" + fr.GetFileLineNumber() + ":" + fr.GetFileColumnNumber();
        //            }
        //            else
        //            {
        //                string prevStackFrameString = prevStackFrame == null? String.Empty : prevStackFrame.ToString();
        //                location = prevMethodName + " at " + fr.GetFileName() + ":" + fr.GetFileLineNumber() + ":" + fr.GetFileColumnNumber()
        //                + " prev: " + prevStackFrameString.Trim();
        //            }

        //            break;
        //        }
        //        prevMethodName = fr.GetMethod().Name;
        //        prevStackFrame = fr;
        //    }

        //    //TODO: make frames a string list
        //    //var frameString = string.Join(";", frames);
        //    //var location = frameString;

        //    var locationToInsert = knownLocationString.Contains(location) ? knownLocationString : location + ";" + knownLocationString;
        //    CallContext.LogicalSetData("torch", locationToInsert);
        //    //CallContext.LogicalSetData("torch", location);

        //    return false;
        //}
    }
}
