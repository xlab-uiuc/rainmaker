// <copyright file="ImmutableStack.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace Microsoft.Torch.Dynamic.FaultInjection
{
    using System;
    using System.Collections;
    using System.Collections.Generic;

    /// <summary>
    /// Immutable stack.
    /// </summary>
    /// <typeparam name="T">Element type.</typeparam>
    public class ImmutableStack<T> : IEnumerable<T>
    {
        private readonly ImmutableStack<T> stack;
        private readonly T value;

        // Constructors are private to force use of Empty
        private ImmutableStack()
        {
        }

        private ImmutableStack(T value, ImmutableStack<T> stack)
        {
            this.stack = stack;
            this.value = value;
            Count = stack.Count + 1;
        }

        /// <summary>
        /// Gets an empty immutavle stack.
        /// </summary>
        public static ImmutableStack<T> Empty { get; } = new ImmutableStack<T>();

        /// <summary>
        /// Gets top value of the stack.
        /// </summary>
        public T Value
        {
            get
            {
                if (IsEmpty)
                {
                    throw new Exception("List is empty");
                }

                return value;
            }
        }

        /// <summary>
        /// Gets number of items in the stack.
        /// </summary>
        public int Count { get; }

        /// <summary>
        /// Gets a value indicating whether a flag indicating if the stack is empty.
        /// </summary>
        public bool IsEmpty => Count == 0;

        /// <summary>
        /// Push an item into the stack.
        /// </summary>
        /// <param name="value">item to push.</param>
        /// <returns>The new stack after inserting the item.</returns>
        public ImmutableStack<T> Push(T value)
            => new ImmutableStack<T>(value, this);

        /// <summary>
        /// Pops an item from the stack.
        /// </summary>
        /// <returns>The popped item.</returns>
        /// <exception cref="Exception">Exception thrown if the stack is empty.</exception>
        public ImmutableStack<T> Pop()
        {
            if (IsEmpty)
            {
                throw new Exception("List is empty");
            }

            return stack;
        }

        /// <inheritdoc/>
        public IEnumerator<T> GetEnumerator()
        {
            var current = this;
            while (!current.IsEmpty)
            {
                yield return current.Value;
                current = current.stack;
            }
        }

        /// <inheritdoc/>
        IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
    }
}
