---
layout: post
title: 正确的Rust引用类型心智模型
date: 2019-10-28 17:34:27 +0800
category: dev
summary: 这是一篇译文，也是我一直想说的东西。
typora-root-url: ../
typora-copy-images-to: ../media
---

这是一篇译文，翻译自[David Tolnay](https://github.com/dtolnay)的[Accurate mental model for Rust's reference types](https://docs.rs/dtolnay/0.0.6/dtolnay/macro._02__reference_types.html#accurate-mental-model-for-rusts-reference-types)，MIT 协议授权。

Rust的[所有权和借用模型](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html)涉及使用*引用*（references）去操作借来的数据，类型系统区分了两种不同的基本引用类型。在代码中写成 `&T` 和 `&mut T`。

 `&mut T` 一般称为对类型为 `T` 的数据的「可变引用」（mutable reference）。而 `&T` 则是一个对于 `T` 的「不可变引用」（immutable reference）或者「常量引用」（const reference）。这些名字不错，对Rust新手能建立合理的直觉。但这篇文章会讲一些理由来说明，对于新手阶段之后的Rust使用者来说，更好的名字是「共享引用」（shared reference）和「独占引用」（exclusive reference）。

## 初学者的理解

如同 Rust 书中的「[引用和借用](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)」一章所述，函数如果获取了一个不可变引用的参数，那就可以读取引用指向的数据：

```rust
struct Point {
    x: u32,
    y: u32,
}

fn print_point(pt: &Point) {
    println!("x={} y={}", pt.x, pt.y);
}
```



但不允许改变数据：

```rust
fn embiggen_x(pt: &Point) {
    pt.x = pt.x * 2;
}
```

```
error[E0594]: cannot assign to `pt.x` which is behind a `&` reference
 --> src/main.rs
  |
1 | fn embiggen_x(pt: &Point) {
  |                   ------ help: consider changing this to be a mutable reference: `&mut Point`
2 |     pt.x = pt.x * 2;
  |     ^^^^^^^^^^^^^^^ `pt` is a `&` reference, so the data it refers to cannot be written
```

要改变结构的字段或者调用那些修改类方法，参数必须通过 `&mut` 引用获取。

```rust
fn embiggen_x(pt: &mut Point) {
    pt.x = pt.x * 2; // okay
}
```

用Rust写一些玩具程序的话，这种区分，这种「不可变引用」和「可变引用」的术语通常也足够了。

## 散架啦

迟早你会遇到一个库签名，直截了当地相悖于初学者对Rust引用的心智模型。作为一个例子，来看看标准库中 [`AtomicU32`](https://doc.rust-lang.org/std/sync/atomic/struct.AtomicU32.html) 的 `store` 方法的签名：

```rust
impl AtomicU32 {
    pub fn store(&self, val: u32, order: Ordering);
}
```

给一个 u32 值，它原子地将 `AtomicU32` 的中的数字改成了你给的那个。可以像这样调用 `store` 方法：

```rust
static COUNTER: AtomicU32 = AtomicU32::new(0);

fn reset() {
    COUNTER.store(0, Ordering::SeqCst);
}
```

在这个讨论中可以忽略 `Ordering` 参数，它根据[C11 原子操作的内存模型](https://doc.rust-lang.org/nomicon/atomics.html)来运作。

在初学者的心智模型下，`AtomicU32::store` 方法获取自身的不可变引用这件事将会让人感觉浑身难受。确实修改是原子的，但修改不可变引用之下的数据怎么会是正确的呢？如果这是刻意为之，确实会令人感觉很魔法（hacky）甚至危险。为什么这个方法是safe的？为什么不是Undefined Behavior？

这会让前C++程序员想起C++中一些 `const_cast`的滥用，也许作者根本没法保证代码不会因为违背一些幽深的语言法则而在未来炸掉，即使现在代码看上去运作正常。

当然C++中所有像 [`std::atomic<T>::store`](https://en.cppreference.com/w/cpp/atomic/atomic/store) 这样的原子性修改方法只能用于可变引用。通过常量引用来储存值如同预料中那样不会通过编译。

```c++
// C++

#include <atomic>

void test(const std::atomic<unsigned>& val) {
  val.store(0);
}
```

```
test.cc:4:7: error: no matching member function for call to 'store'
  val.store(0);
  ~~~~^~~~~
/usr/include/c++/5.4.0/bits/atomic_base.h:367:7: note: candidate function not viable: no known conversion from 'const std::atomic<unsigned int>' to 'std::__atomic_base<unsigned int>' for object argument
      store(__int_type __i, memory_order __m = memory_order_seq_cst) noexcept
      ^
/usr/include/c++/5.4.0/bits/atomic_base.h:378:7: note: candidate function not viable: no known conversion from 'const std::atomic<unsigned int>' to 'volatile std::__atomic_base<unsigned int>' for object argument
      store(__int_type __i,
      ^
```

有什么地方出了问题。这超出了初学者对Rust `&` 和 `&mut` 引用类型意义的理解。

## 更好的名字

`&T` 不是对那些类型为 `T` 的数据的 「不可变引用」或者「常量引用」，而是「共享引用」。`&mut T` 不是「可变引用」而是「独占引用」。

独占引用意味着在同一时刻，同一个值不可能存在别的引用。共享引用则意味着*可能*存在对同一个值的其它引用，也许是在别的线程（如果 `T` 实现了 `Sync` 的话）或是当前线程的调用栈中。Rust 借用检查器的一个关键职能就是确保独占引用真的是独占性的。

再看看 `AtomicU32::store` 的签名。

```rust
impl AtomicU32 {
    pub fn store(&self, val: u32, order: Ordering);
}
```

对于函数用共享引用获取原子式的u32，此时应该**感到完全自然**。同一时刻对同一个 `AtomicU32` 有别的引用当然没问题。原子性就是为了并发读写而不导致数据争用（data race）而存在的。如果库在调用 `store` 时不允许别的引用存在，那就没什么理由用原子性了。

独占引用一直是可变的原因是如果没有别的代码看着同一个数据，我们可以大胆地修改数据而不引发数据争用。数据争用（data race）是指多个地方同时操作同一个数据，并且至少有一个在修改，从而产生意外的结果或者内存不安全的情况。但是通过原子性或者下述内部可变性的方式，通过共享引用修改数据也是安全的。

充分内化「共享引用」和「独占引用」，学会这样思考，是学会充分利用Rust与其强大的安全性保证的重要一步。

## 怎么教

一开始将 `&`  和 `&mut` 作为不可变和可变来介绍的做法，我不觉得不好。学习曲线就经足够难了，即使不算上本文的内容。对于初学者而言，修改能力的不同是两种引用类型最显著的实际差异。

我觉得建立从「不可变引用」/「可变引用」到「共享引用」/「独占引用」的心智模型转变是必要的一步。应该鼓励初学者在正确的时间走出这一步，而本页可以帮助他们走出这一步。当有人困惑于一些库函数预料需要 `&mut` 却只获取 `&` 时，就是发本页链接的好时机了。

在内化了共享和独占引用之后，我觉得继续说「可变引用」也不错，毕竟关键字是 `mut`。只要别忘了共享引用背后的数据有时也*可能*是可变的。另一方面，对于共享引用，我建议始终说「共享引用」而不是「不可变引用」或者「常量引用」。

## 附录：内部可变性

在Rust中，术语「内部可变性」（interior mutability）表示支持通过共享引用修改数据。

我用 `AtomicU32` 作为例子的缘故是当你从初学者的心智模型切换到正确的心智模型时，它最能唤起从「浑身难受」到「完全自然」的深刻转变。尽管原子性是多线程代码的重要一块，但内部可变性在单线程中也同样重要。

通过共享引用持有可变数据的*唯一*方法是标准库类型 [`UnsafeCell<T>`](https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html) 。它是一种 unsafe 的底层工具，一般不会直接去使用。所有别的内部可变性方式都是建立在它之上的安全抽象，有着不同的性质和需求，适用于不同的情况。（根本上来说，Rust就是一个建立安全抽象的语言，而内部可变性就是其中一个最明显的部分。）

除了原子操作以外，其它建立在内部可变性上的标准库安全抽象还包括：

* [`Cell<T>`](https://doc.rust-lang.org/std/cell/struct.Cell.html)： 修改是安全的，哪怕可能存在其它对同一个 `Cell<T>` 的引用，因为API施行：
  * 多个线程不可能同时持有对同一个 `Cell<T>` 的应用，因为 `Cell<T>` 没有实现 `Sync` trait，也就是说 `Cell<T>` 是单线程的；
  * 不可能获取对 `Cell<T>` 中的内容的引用，因为这种引用可能因为修改而失效，作为替代所有的访问通过复制数据来完成。
* [`RefCell<T>`](https://doc.rust-lang.org/std/cell/struct.RefCell.html)：修改是安全的，哪怕可能存在其它对同一个 `RefCell<T>` 的引用，因为API施行：
  * 类似 `Cell<T>`，`RefCell<T>` 是单线程的，所以不同的线程不可能引用同一个值。
  * 在一个线程之内，当有读者持有内容的引用时，运行时的借用检查会阻止对内容的修改。
* [`Mutex<T>`](https://doc.rust-lang.org/std/sync/struct.Mutex.html)：修改是安全的，哪怕可能存在其它对同一个 `Mutex<T>` 的引用，因为API施行：
  * 同一时刻只有一个引用可以对内部的 `T` 读写。其他访问会被阻塞到现在的引用释放了锁为止。
* [`RwLock<T>`](https://doc.rust-lang.org/std/sync/struct.RwLock.html)：修改是安全的，哪怕可能存在其它对同一个 `RwLock<T>` 的引用，因为API施行：
  * 同一时刻只有一个引用可以用来修改 `T`，且仅当此时没有别的引用在被读。