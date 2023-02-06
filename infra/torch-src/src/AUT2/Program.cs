using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AUT
{
    class Program
    {
        static void Main(string[] args)
        {
            //sJsonTest.test();
            Benchmark();
            //AsyncBenchmark();
        }

        static void AsyncBenchmark()
        {
            Task.Run(() => 0).ContinueWith((t) => 1);
            Console.WriteLine();
        }

        static void Benchmark()
        {

            Test.SayHello();

            // static functions
            Test.TestParams();
            Test.TestShortStaticInt(5, "hello", new Random());
            Test.TestShortStaticObject(5, "hello", new Random());
            Test.TestShortStaticObjectNoArgs();
            Test.TestShortStaticString(5, "hello", new Random());
            Test.TestShortStaticVoid(5, "hello", new Random());
            Test.TestStaticInt(5, "hello", new Random());
            Test.TestStaticObject(5, "hello", new Random());
            Test.TestStaticObjectNoArgs();
            Test.TestStaticString(5, "hello", new Random());
            Test.TestStaticVoid(5, "hello", new Random());


            Test test = new Test(10);
            test.TestShortInt(5, "hello", new Random());
            test.TestShortObject(5, "hello", new Random());
            test.TestShortObjectNoArgs();
            test.TestShortString(5, "hello", new Random());
            test.TestShortVoid(5, "hello", new Random());
            test.TestInt(5, "hello", new Random());
            test.TestObject(5, "hello", new Random());
            test.TestObjectNoArgs();
            test.TestString(5, "hello", new Random());
            test.TestVoid(5, "hello", new Random());

        }

    }

    public class Test
    {
        public int id = 10;
        public Test(int id)
        {
            this.id = id;
        }

        public static void SayHello()
        {
            Console.WriteLine("Hello world!");
        }

        public static void TestParams()
        {
            int i = -1;
            TestParamsInternal('x', -1, -1, -1, -1, -1, "x", DateTime.MinValue, new List<int> { 1, 2, 3 }, out int x, ref i);
        }
        public static void TestParamsInternal(char c, short s, int i, long l, float f, double d, string st, DateTime dt, List<int> list, out int outInt, ref int refInt)
        {
            outInt = -100;
            Console.WriteLine($"{c};{s};{i};{l};{f};{d};{st};{dt};{list.Count};{outInt};{refInt}");
            refInt = 200;
            c = 'x';
            s = -1;
            i = -1;
            l = -1;
            f = -1;
            d = -1;
            st = "bye";
            dt = DateTime.Now;
            list = new List<int>();
            Console.WriteLine(s + " " + st);
        }

        // static methods with a short header
        public static void TestShortStaticVoid(int x, string y, object z)
        {

        }

        public static int TestShortStaticInt(int x, string y, object z)
        {
            return x;
        }

        public static string TestShortStaticString(int x, string y, object z)
        {
            return y;
        }

        public static object TestShortStaticObject(int x, string y, object z)
        {
            return z;
        }

        public static object TestShortStaticObjectNoArgs()
        {
            return new List<string> { };
        }


        // instance methods with a short header
        public void TestShortVoid(int x, string y, object z)
        {

        }

        public int TestShortInt(int x, string y, object z)
        {
            Console.WriteLine("X = " + x);
            return x;
        }

        public string TestShortString(int x, string y, object z)
        {
            return y;
        }

        public object TestShortObject(int x, string y, object z)
        {
            return z;
        }

        public object TestShortObjectNoArgs()
        {
            return new List<string> { };
        }


        // static methods with a short header
        public static void TestStaticVoid(int x, string y, object z)
        {
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();
        }

        public static int TestStaticInt(int x, string y, object z)
        {
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

            return x;
        }

        public static string TestStaticString(int x, string y, object z)
        {
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

            return y;
        }

        public static object TestStaticObject(int x, string y, object z)
        {
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

            return z;
        }

        public static object TestStaticObjectNoArgs()
        {
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

            return new List<string> { };
        }


        // instance methods with a short header
        public void TestVoid(int x, string y, object z)
        {
            //Console.WriteLine("Recieved param: " + x);
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

        }

        public int TestInt(int x, string y, object z)
        {
            //Console.WriteLine("Recieved param: " + x);
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

            return x;
        }

        public string TestString(int x, string y, object z)
        {
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

            return y;
        }

        public object TestObject(int x, string y, object z)
        {
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

            return z;
        }

        public object TestObjectNoArgs()
        {
            Random r = new Random();
            List<int> dummy = new List<int>();
            for (int i = 0; i < 10; i++)
                dummy.Add(r.Next());
            dummy.Sort();

            return new List<string> { };
        }

        //public int TestIntWithException()
        //{
        //    try
        //    {
        //        return 5;
        //    } catch (Exception e)
        //    {
        //        if (e is FileNotFoundException)
        //            throw;

        //        throw new InvalidCastException();
        //    }
        //}


        //public object TestObjWithException(string s)
        //{
        //    try
        //    {
        //        return new Random();
        //    }
        //    catch (Exception e)
        //    {
        //        return DateTime.Now;
        //    }
        //}

        public static Task Delay(int ms)
        {
            return Task.Delay(ms);
        }


    }

    public class Foo
    {
        public void Bar()
        {
            Console.WriteLine("Invoked Foo.bar");
        }
    }
}
