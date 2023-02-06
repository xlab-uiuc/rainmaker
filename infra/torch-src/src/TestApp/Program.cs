using System;
using Microsoft.Torch.Dynamic.FaultInjection;

namespace TestApp
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hit any key to continue");
            Console.ReadKey();
            InjectContext ic = new InjectContext();
            Exception e;
            object retValue = null;
            object c;
            ic.OnBegin(new object(), "method", new object[0], out e, out retValue, out c);
            Console.WriteLine("Hello World2!");
        }
    }
}
