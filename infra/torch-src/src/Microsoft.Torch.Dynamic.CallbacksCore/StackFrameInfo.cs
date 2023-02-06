namespace Microsoft.Torch.Dynamic.FaultInjection
{
    public class StackFrameInfo
    {
        public string Method { get; set; }
        public string FileName { get; set; }
        public int Line { get; set; }
        public bool IsAsyncMethod { get; set; }

        public StackFrameInfo(string method, bool isAsync, string file, int line)
        {
            Method = method;
            IsAsyncMethod = isAsync;
            FileName = file;
            Line = line;
        }

        public override string ToString()
        {
            return $"{Method} at {FileName}:{Line}";
        }
    }
}
