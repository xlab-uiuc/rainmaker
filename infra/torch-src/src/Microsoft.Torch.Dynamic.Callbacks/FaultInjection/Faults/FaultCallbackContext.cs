namespace Microsoft.Torch.Dynamic.FaultInjection
{
    /// <summary>
    /// Context passed between OnStart() and OnEnd().
    /// </summary>
    public class FaultCallbackContext
    {
        /// <summary>
        /// Gets or sets fault rule applied.
        /// </summary>
        public FaultRule FaultRule { get; set; }

        /// <summary>
        /// Gets or sets additional information passed from OnStart() to OnEnd();
        /// </summary>
        public object State { get; set; }
    }
}
