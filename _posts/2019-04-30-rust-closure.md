---
layout: post
title: 理解 Rust 中的 Closure
date: 2019-04-30 17:18:55 +0800
category: dev
summary: 最近复习了一下 Rust 中的closure，笔记如下。
typora-root-url: ../
typora-copy-images-to: ../media
---

Rust中的closure（闭包函数），很难用！这里记录下重要的事情。

## 原理

一些语言中没有closure和普通函数的区分，但Rust有。对Rust来说普通函数就是一段代码。而closure和 C++ 类似：每个closure会创建一个匿名的 `struct`，编译器会在当前<ruby>上下文 <rt>Context</rt></ruby>捕获closure代码中的外部变量然后塞进这个<ruby>结构体 <rt>Struct</rt></ruby>里面。

**这件事非常重要**，请默念三遍*一个closure就是一个捕获了当前上下文变量的结构体*（外加一段代码，这不重要）。

这解释了为什么Rust中两个参数和返回值一样的closure不被视作同一类型[^not-same-type]，因为它们背后的匿名结构体不同，有着不同的大小、字段和lifetime。

[^not-same-type]: 其实所有的普通函数也都是唯一的类型。被视作 [Zero Sized Types](https://doc.rust-lang.org/nomicon/exotic-sizes.html#zero-sized-types-zsts)。

```rust
let m = 1.0;
let c = 2.0;

let line = |x| m*x + c;

// 等价于

struct SomeUnknownType<'a> {
    m: &'a f64,
    c: &'a f64
}

impl<'a> SomeUnknownType<'a> {
    fn call(&self, x: f64) -> f64 {
        self.m * x + self.c
    }
}
```

例子来源于[Why Rust Closures are (Somewhat) Hard](https://stevedonovan.github.io/rustifications/2018/08/18/rust-closures-are-hard.html)。

这也是closure难用的根源：

1. Rust中结构体的可变性以及liftime本身就很烦人。

2. Closure的规则都是隐式的：closure捕获值的方式及所生成的closure的类型都是按照隐式的规则决定的。

3. Closure一直会捕获整个复合类型，如 `struct`, `tuple` 和 `enum` 。而不只是单个字段。[2]

对于 (3)，[Rust团队已经接受了一个提案](https://github.com/rust-lang/rfcs/blob/master/text/2229-capture-disjoint-fields.md)，旨在改进不相交字段的捕获规则。（当前看起来没多少进展）

### 为什么

对于 (1) 和 (2) 是语言设计思路所带来的结果，为什么会这样呢？

因为closure很好用，但是我们不想付出运行时代价。所有语言都有类似的东西，但是它们把closure捕获的结构丢到堆上以保证所有closure类型大小一样，且借助了GC管理资源。

Rust选择「<ruby>零<rt>Zero</rt>额外开销<rt>Overhead</rt></ruby>」所以必须用这种方式来实现closure。使用高级抽象的同时保持了性能无损。比如说我们能用很函数式的方法处理迭代器，但最后生成的汇编和手写循环没什么区别。

并且Rust提供了 `Box<Fn() -> T>` 和 `Rc`让你可以手动做到别的语言自动做到的事情。你需要显式使用这些设施，因为这代表额外的开销。

而选择隐式的捕获规则是因为closure被设计为在某个特定上下文内以短小、简洁而频繁的方式书写[^2]，所以采用了这种隐式且最保守的捕获方式。代价就是容易让人摸不着头脑。虽说利大于弊，但的确是一个缺点（参见下一节的边栏部分）。

[^2]: 比如参数和返回值类型都可以省略。

## 规则

捕获规则最简单的情形是 `move || {...}` 它会尝试获取closure中用到的值的ownership，如果值是 `Copy` 的则 copy 一个。

而默认的捕获方式是：

1. 如果可以，则尽量用 `&` 借用
2. 否则，如果可以，则总是 `&mut` 借用
3. 最后，无计可施必须要ownership的话，才会move

<aside>

以下内容可以跳过。

即使是面临必须要ownership的情况，如果值可以 `Copy`，编译器依然会避免move，而是用 `&` 的方式借用值，之后在需要的时候 `*`。相关文章是《[Rust 闭包环境捕获行为与 Copy trait](https://iovxw.net/p/rust-closure-and-copy/)》。

我们都认为是 bug，直到[语言团队成员回复说这是预料中的行为](https://github.com/rust-lang/rust/issues/60413#issuecomment-487965668)。之后我注意到这是规则1较为反直觉的特例。

</aside>

捕获之后，根据<ins>你在closure代码中**如何使用捕获到的值**</ins>，编译器会为closure实现函数traits。最后实现了哪些traits和捕获的方式（有没有加 `move`）<ins>或者捕获到了哪些变量是无关的</ins>。

* 所有函数都至少能调用一次，所以全都会实现 `FnOnce`。
  * 另外，对于那些*不会**移走**匿名结构体中变量*的closure实现 `FnMut`。
    * 并且，对于那些*不会**修改**匿名结构体中变量*的closure实现 `Fn`。

下图中可以看出这三者是包含的关系。

[![Rust - Closure](/media/Rust - Closure.png)](https://docs.google.com/drawings/d/1yuCkfuHW693Lg93in3Vk_hvIwJIQeOsfkX_2q5sC5H8/edit?usp=sharing)



其中 `FnMut` 和 `Fn` 能调用多次。 `FnMut` 调用时需要对自己匿名结构体的 `&mut self` 引用。调用 `Fn` 只需要 `&self` 引用就足够了。

## 实践

现在我们写下不同类型的closure。然后去看编译器产出的MIR。

MIR是中级中间表示（简称中二表示）详细可以看[官方博客的这篇文章](https://blog.rust-lang.org/2016/04/19/MIR.html)。我们关注的只是少部分内容，大部分看不懂也没关系。

总而言之，MIR告诉我们「代码究竟会变成什么样」但又保留了类型信息，不像汇编那样面目全非。

### FnOnce

Closure中必须移走某个变量的ownership，这种closure需要 `self` 来执行，所以只能 `FnOnce`。[Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2018&gist=49be2b83ebe6e9dc7c85fb833c7fd9d5) （点右上角“RUN”按钮旁的「…」按钮，再点 “MIR” 看结果。）

```rust
fn main() {
    let homu = Homura;
    let get_homu = || homu;
    get_homu();
}
```

调用时的 MIR

```rust
let mut _4: [closure@src/main.rs:9:20: 9:27 homu:Homura];
let mut _5: ();
_3 = const std::ops::FnOnce::call_once(move _4, move _5) -> bb1;
```

可以看到它是以 `FnOnce` 方式调用的。

`_4` 作为第一个参数传进去，它的类型 `[closure@src/main.rs:10:20: 10:27 homu:Homura]` 就是本文一直在叨念的匿名结构体了。其中 `home:Homura` 则是这个结构体捕获的变量和她的类型。

`_5` 代表着无参数。

Closure代码所编译成的普通函数：

```rust
fn main::{{closure}}(_1: [closure@src/main.rs:9:20: 9:27 homu:Homura]) -> Homura {
    let mut _0: Homura;                  // return place

    bb0: {                              
        _0 = move (_1.0: Homura);        // bb0[0]: scope 0 at src/main.rs:9:23: 9:27
        return;                          // bb0[1]: scope 0 at src/main.rs:9:27: 9:27
    }
}
```
注意这里 `_1` 的类型：`[closure@src/main.rs:9:20: 9:27 homu:Homura]` 前没有 `&` 或者 `&mut`，代表这个调用后会消耗掉匿名结构体。

`_0 = move (_1.0: Homura);` 可以看见内部移走了 `homu`。

### FnMut

在closure中修改某个可变的引用[^exception]，但无需移走任何捕获到的值。这种closure必须请求一个 `&mut`，所以有 `FnMut`。 [Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2018&gist=ec4a6dfb4373776899a44d4ab6f5efb7)

[^exception]: 有一种[符合直觉的例外在这里](https://doc.rust-lang.org/reference/types/closure.html#unique-immutable-borrows-in-captures)。

```rust
fn main() {
    let mut madoka: Option<Madoka> = Some(Madoka);
    let mut disappear = || madoka = None;
    disappear();
}
```

调用时：

```rust
let mut _6: &mut [closure@src/main.rs:9:25: 9:41 madoka:&mut std::option::Option<Madoka>];
let mut _7: ();
_5 = const std::ops::FnMut::call_mut(move _6, move _7) -> bb1;
```

Closure 所生成的函数体：

```rust
fn main::{{closure}}(_1: &mut [closure@src/main.rs:9:25: 9:41 madoka:&mut std::option::Option<Madoka>]) -> () {
	// ...
}
```

可以看到 `_1` 变成一个 `&mut` 引用了。能多次调用而不会消耗匿名结构体。

被捕获的值变成了 `madoka:&mut std::option::Option<Madoka>` 。于是在这个 closure 销毁之前别人都不能访问 `madoka` 了。

### Fn

在closure中只会读取外部的值，只需要 `&self` 就能执行，当然全部三种都实现了。


```rust
fn main() {
    let homu = Homura;
    let mado = Madoka;
    let marry = || (&homu, &mado);
  	marry();
}
```

[Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2018&gist=111e670f19717bfb7331e38e206bb165) 

调用时：

```rust
let mut _7: &[closure@src/main.rs:10:17: 10:34 homu:&Homura, mado:&Madoka];
let mut _8: ();
_6 = const std::ops::Fn::call(move _7, move _8) -> bb1;
```

是用 `Fn` 的方式调用的。

Closure 生成的函数体：

```rust
fn main::{{closure}}(_1: &[closure@src/main.rs:10:17: 10:34 homu:&Homura, mado:&Madoka]) -> (&Homura, &Madoka) {
	// ...
}
```

如果closure根本不捕获任何东西，则匿名结构体是[Zero Sized Types](https://doc.rust-lang.org/nomicon/exotic-sizes.html#zero-sized-types-zsts)，在运行时不会被创建。这类closure等价于普通函数，自然也实现了全部三种。代码略。

### 实现哪些 traits 和捕获到的值无关

就算用 `move` 强制捕获变量的所有权，只要不移走它而仅仅是修改或读取它。这种情况依然会实现 `FnMut` 或 `Fn`。[Playground](https://play.rust-lang.org/?version=stable&mode=debug&edition=2018&gist=4e5061559d9d80ac364278e33caed614)

```rust
fn main() {
    let homu = Homura;
    let mado = Madoka;
    let marry = move || {
        (&homu, &mado);
    };
    marry();
}
```

这种代码，用了 `move`  所以会捕获 `homu` 和 `mado` 的所有权，但是MIR可以看到是通过 `Fn::call` 调用的：

```rust
let mut _5: &[closure@src/main.rs:10:17: 12:6 homu:Homura, mado:Madoka];
let mut _6: ();
_4 = const std::ops::Fn::call(move _5, move _6) -> bb1;
```

看看closure所生成的函数体吧：


```rust
fn main::(_1: &[closure@src/main.rs:10:17: 12:6 homu:Homura, mado:Madoka]) -> () {
    let mut _0: ();                      // return place
    let mut _2: (&Homura, &Madoka);
    let mut _3: &Homura;
    let mut _4: &Madoka;

    bb0: {                              
        // ...
        _3 = &((*_1).0: Homura);
        StorageLive(_4);
        _4 = &((*_1).1: Madoka);
        (_2.0: &Homura) = move _3;
        (_2.1: &Madoka) = move _4;
        // ...
        return;
    }
}
```

不同于前一个没有加 `move` 的例子。`homu:Homura` 和 `mado:Madoka` 前**没有** `&`，代表匿名结构体捕获了这两个变量的所有权。

然而捕获了那些变量的匿名结构体本身又是以 `_1: &[closure...]` 的方式传入的。因为函数体内根本不会移走 `homu` 或者 `mado`。

如果修改这份代码在 closure 过程内修改 `mado` 的话会变成什么样呢？留作习题。

----------

*感谢 Telegram「Rust 众」群网友们对本文的帮助。*

## 参考阅读

1. [Why Rust Closures are (Somewhat) Hard](https://stevedonovan.github.io/rustifications/2018/08/18/rust-closures-are-hard.html)
2. [Closure types](https://doc.rust-lang.org/reference/types/closure.html)
3. [`std::ops::{Fn, FnMut, FnOnce}`](https://doc.rust-lang.org/std/ops/index.html)
4. [闭包 - Rust编程](https://zhuanlan.zhihu.com/p/23710601)
5. [Higher-Rank Trait Bounds (HRTBs)](https://doc.rust-lang.org/nomicon/hrtb.html)

## 脚注