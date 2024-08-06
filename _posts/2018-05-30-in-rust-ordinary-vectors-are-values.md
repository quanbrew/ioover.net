---
layout: post
title: Rust中，常规的vector是一种值
# date: 2018-05-30 00:46:42
category: dev
summary: 讲解了不可变的 Persistent Data Structure 以及对于 Rust 意味着什么。
typora-root-url: ../
typora-copy-images-to: ../media
---

[原文地址](http://smallcultfollowing.com/babysteps/blog/2018/02/01/in-rust-ordinary-vectors-are-values/) 作者：Niko Matsakis

*本文不需要Rust基础也能阅读*。其中vector指的是<del>大多数</del>很多语言中的List或者动态数组。

------

我最近一直在思考持久化容器(persistent collections)，特别是它们与Rust的关系，我想写下一些我的观察。[^1]

[^1]: 正好，我之前写的SLG求解器似乎特别喜欢用持久化容器



## 什么是持久化容器

传统上，持久化容器被看作是一种与众不同的建立容器的方法。传统的容器有类似`push`的方法，能让vector**原地**增长：

```rust
vec.push(element); // 往 `vec` 增加元素
```

而持久化容器有类似`add`的方法，能保留原本的vector不动，而返回一个已经被修改的**新vector**：

```rust
let vec2 = vec.add(element);
```

此处的关键特性在于`vec`没有改变，这使得持久化容器非常适合函数式语言（以及适合并行计算）。

## 持久化容器如何运作

我不会详细介绍任何特定的设计，但是大多数都是基于某种树的。比如说，如果有一个vector类似于`[1, 2, 3, 4, 5, 6]`，可以想象一下，这些值不是以一大块的方式储存，而是将它们储存在某种树中，值保存在叶子结点里。在下面的示意中，元素被分开放在两个叶子结点，父节点的指针指向这两个节点：

```
 [*        *] // <-- 这是 vector 的父节点
  |        |
-----    -----
1 2 3    4 5 6
```

现在想想我们要改变vector中的一个值，比如说我们想把`6`改成`10`。这意味着我们必须改变右节点，但可以继续使用左节点。所以我们创建一个新的父节点，这样就能引用新的右节点。

```
 [*        *]   // <-- 原 vector
  |        |    //     (仍然存在，没有被改变)
-----    -----
1 2 3    4 5 6
-----
  |      4 5 10 // <-- 右节点的新拷贝
  |      ------
  |        |
 [*        *]   // <-- 新的 vector
```

对于一个平衡的树中，这通常意味着往一个持久化vector中插入元素往往是 $$O(\log n)$$ ——我们必须复制和修改一些叶子，然后必须复制和修改所有这条路径的父节点。**这比修改传统的vector开销更大，修改传统的vector只是一些CPU指令。**

一些意见：

- 如果这个vector实际上没有[别名](https://zh.wikipedia.org/wiki/%E5%88%AB%E5%90%8D_(%E8%AE%A1%E7%AE%97))（多处引用同一段内存），并且你知道它没有别名，那么你常常可以避免这些复制，仅仅是原地修改树。稍后，我会谈到 [`DVec`](https://docs.rs/dogged/0.2.0/dogged/struct.DVec.html)，一个试验性的Rust持久化容器库做到了这个特性。但在典型的基于GC的语言中很难做到，因为你永远不知道自己在用的是别名。
- 持久化容器有非常多的其他设计，一些设计偏向于特定的使用模式。比如说，[这篇论文](https://www.lri.fr/~filliatr/ftp/publis/puf-wml07.pdf)提出一中针对于类似Prolog的程序的设计；这个设计内部用了可变性实现 $$O(1)$$ 插入，但是在接口上对用户隐藏。当然，这些低开销的插入是有代价的：数据结构的较老的拷贝使用起来开销很大。

## 持久化容器让容器变成值

某些情况下，持久化容器能让代码更容易被理解。因为他们更像一个「普通的值」，没有自己的「秉性」。来看这个JS代码，用整数：

```javascript
function foo() {
    let x = 0;
    let y = x;
    y += 1;
    return y - x;
}
```

此处我们修改 `y` 的时候，不期望 `x` 也改变，因为 `x` 只是一个简单的值。但是如果改成用数组：

```javascript
function foo() {
    let x = [];
    let y = x;
    y.push(22);
    use(x, y);
}
```

现在修改`y`，`x`也会跟着改变。也许这正是我们想要的，但有时候不是。当vector藏在对象后面的时候，事情会愈发让人摸不清头脑：

```javascript
function foo() {
    let object = {
        field: []
    };
    ...
    let object2 = {
        field: object.field
    };
    ...
    // 现在 `object.field` 和 `object2.field` 在幕后秘密相连
    ...
}
```

不要误会，有时候`object.field`和`object2.field`是指向同一个vector是非常方便的。但另一些时候这不是你想要的。我常常发现改成持久化容器能让我的代码更清晰、易于理解。

## Rust 是特别的

如果曾看过一次我对于Rust的演讲[^2]，就会知道我反复强调Rust设计的一个核心要素：

[^2]: 如果还没有，那么我觉得[这个](https://www.sics.se/nicholas-matsakis)非常好。



> 数据分享和可变：都是好东西，但放在一起就非常可怕。

基本上，这个想法是，当有两个不同的路径访问同样的内存（在上一个例子中的`object.field`和`object2.field`），对它进行修改就是非常危险的意图。当在Rust中试图放弃使用GC，情况就尤其如此，因为突然不清楚谁应该管理这块内存了。**但哪怕使用GC也是如此**，因为一个像`object.field.push(...)`的修改可能影响比预料中更多的对象，从而导致错误（尤其是但不限于发生在并行线程中的情况）。

那么，如果试图两次访问同一个vector，在Rust中会发生什么？回到刚刚看到的JavaScript例子，但这次使用Rust写。第一个例子是用整数，运作得和JS一样：

```rust
let x = 0;
let mut y = x;
y += 1;
return y - x;
```

但第二个用vector的例子，根本不会通过编译：

```rust
let x = vec![];
let mut y = x;
y.push(...);
use(x, y); // ERROR: use of moved value `x`
```

问题在于，一旦我们用了 `y = x`，就已经拿走了 `x` 的所有权，这样它就不能再被使用了。

## 在Rust中，普通的vector是值

可以引出结论。在Rust中，我们日常使用的「普通的容器」**已经像值一样行事**：实际任何Rust类型都是如此——只要不使用`Cell`或者`RefCell`。换句话说，假设你的代码通过编译，你知道你的vector没有在多个地方被修改：你可以用一个整数来代替它，而它会有相同的行为。这样很好。

**这意味着就Rust而言，持久化容器和普通容器相比，不必一定要有「不同的接口」。**例如，我创建了一个名为[dogged](https://crates.io/crates/dogged)[^3]的持久化vector。Dogged提供了一种称为 [`DVec`](https://docs.rs/dogged/0.2.0/dogged/struct.DVec.html) 的vector类型，它基于[Clojure提供的持久化vector](https://hypirion.com/musings/understanding-persistent-vector-pt-1)。但如果看看 [`DVec`](https://docs.rs/dogged/0.2.0/dogged/struct.DVec.html) 提供的方法，会发现这是一种标准的容器（有 `push` 等等）。


[^3]: 在英语中，如果你“dogged”地追求目标，就很坚持不懈（persistent）。

比如说这是一种 `DVec` 的有效操作：

```rust
let mut x = DVec::new();
x.push(something);
x.push(something_else);
for element in &x { ... }
```

尽管如此，一个`DVec`还是一个持久化数据结构。在实现上，一个 `DVec` 被实现为[Trie](https://zh.wikipedia.org/wiki/Trie)。它包含一个 [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) （引用计数指针）来引用其内部数据。当调用`push`时，我们会更新`Arc` 指向新的vector，并把旧数据留在原地。

（顺便说一句，[`Arc::make_mut`](https://doc.rust-lang.org/std/sync/struct.Arc.html#method.make_mut)是一个**非常酷的**方法。它检查`Arc`的引用计数：如果是1，则给你对内容的唯一（可变）访问权限；如果引用计数**不是**1，那么它将复制`Arc`（及其内容），并给你这个复制的数据的可变引用。如果你回想起持久化数据结构是如何运作的，就能发现这对于更新一个树是*完美的*，在容器没有别名的情况下，它可以避免复制操作。）

## 但持久化容器间是不同的

一个 `Vec` 和一个 `DVec` 之间的主要区别不是它们提供的操作，而在于**它们的开销**。也就是说，在一个标准的`Vec`上`push`时，它是一个$$O(1)$$操作。当复制它的时候，就是 $$O(n)$$。对于一个`DVec`，开销截然不同：`push`是 $$O(\log ⁡n)$$，但是复制是 $$O(1)$$。

**尤其对于一个DVec，clone操作只是增加内部的Arc引用计数，而对于普通vector，clone必须复制所有数据。**当然，对一个`DVec`执行`push`，会在重建树受影响的部分时复制一部分数据（而`Vec`一般只需要在数组末尾写入数据）。

众所周知，「大O」记法只描述渐进耗时。`DVec`我已经遇到的一个问题在于，在性能上它很难与标准的`Vec`竞争。单纯地整串复制数据经常比更新树以及分配内存要快。我发现只有在极端情况下才有用`DVec`的理由——比如说做大量复制操作，或者有大量数据。

当然不全关于性能。如果进行大量复制操作，`DVec` 也应该使用更少的内存，因为大量内部数据可以共享。

## 结论

在这里我通过持久化容器试图说明，Rust的所有权系统是如何以一种巧妙的方式，将函数式风格和命令式风格融合。**也就是说，Rust的标准容器虽然以典型的命令式接口实现，但实际上它们像是「值」一样在运作：**将一个vector从一个地方赋值到另一个地方，如果想继续使用原本的那个，则必须`clone`它，这就使得新的拷贝独立于旧的那个。

这不是新的见解。比如说1990年，Phil Wadler写了一篇[题为《线性类型可以改变世界！》的论文](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.55.5439&rep=rep1&type=pdf)，在这之中他得出几乎一摸一样的结论，然而是从相反的起点出发。在论文中他说，依旧能提供一个持久化的接口（例如，`vec.add(element)`返回新vector的方法），但如果使用线性类型，可以通过一个命令式的数据结构暗地里实现它（例如`vec.push(element)`），而不让别人知道。

在摆弄`DVec`的时候，我发现一个持久化vector也提供常规（命令式）接口是很有用的。比如说，我能够非常容易修改[ena 合一库](https://crates.io/crates/ena)（在内部它基于一个vector）让它运作在持久化模式（使用`DVec`）或者命令式模式（使用`Vec`）。基本的点子是将具体的vector类型泛型化，如果这些类型提供一样的接口的话这会很简单。

（另外，我乐意看到更多的实验。比如说，如果一个vector开始时是一个常规vector，但是超过某个长度就会变成持久化vector，我认为是非常有用的。）

*特别*对于Rust，我觉得有其他的原因让人对持久化容器产生兴趣。同时对数据进行分享和修改是一种有风险的模式，但有时候是必要又有用的，而在Rust现在用起来感觉是反人类的。**我认为我们应该做一些事情来改善这种情况，我也有一些具体的想法**[^4]，但我觉得在这里使用「持久化 vs 命令式容器」的表述是不合理的。换句话说，Rust已经*有了*持久化容器，它只是在`clone`操作上特别低效。

[^4]: 具体的想法，必须等到下一篇博客文章。现在是让我女儿去上学的时间了！

