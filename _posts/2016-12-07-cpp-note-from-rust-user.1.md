---
title: C++ 学习笔记（一）
layout: post
category: dev
toc: true
summary: 原本的标题是「Rust 使用者的C++学习笔记」，感觉口气太大了就写学习笔记吧
---

原本的标题是「Rust 使用者的 C++学习笔记」，感觉口气太大了就写学习笔记吧，参考书只有 《C++ Primer》，会有很多对照Rust的部分，就当是自己写给自己看的，每句话都感觉可能错的离谱… <!--more-->

## 原生类型

~~~c++
#pragma once
#include <cstddef>
#include <cstdint>
#include <type_traits>
// Type redefinition
using i8 = std::int8_t;
using i16 = std::int16_t;
using i32 = std::int32_t;
using i64 = std::int64_t;
using u8 = std::uint8_t;
using u16 = std::uint16_t;
using u32 = std::uint32_t;
using u64 = std::uint64_t;
using isize = std::make_signed_t<std::size_t>;
using usize = std::size_t;
using iptr = std::intptr_t;
using uptr = std::uintptr_t;
using f32 = float;
using f64 = double;
~~~

这是C++学习项目里面的类型重定义，感觉可以用在不少C++项目里面来简化，毕竟 `size_t` 对比 `isize` 多了一个下划线不是吗？

Rust将`int`类型改名成`isize`，因为这种类型的大小会根据机器位数不同而不同，不注意的话会是很多 bug 的源泉，因为`isize`比`int`要多两个字符，所以人们不会想当然的写`isize` ，而是根据场合不同而用固定长度的类型。

这种方式我觉得在C++里也是好的习惯，`int` 乱飞应该不是个好事。

## 类型转换

Rust里面禁止了一切隐式类型转换，而C++不是这样，有几点值得注意的：

* `bool` 的转换逻辑和C一样，非0值为 `false` 其余皆为 `true`。
* 浮点数转换成整数是抹去小数部分，也就是说是 `floor`。
* 超过容量的数，转换为无符号整型是取模，转换为有符号整型是UB，实践中大多数应该是负溢出。（但是格式化你的硬盘也是符合标准的行为……）
* 整型提升，这是个大坑，两个小整形（哪怕类型一样）的算术运算结果，至少会放在 `int` 里面，再根据上下文再转换类型。可以试试 `sizeof(c+c)` 其中 `c` 是 `char` 类型的。

`i8`转换到`i32`是很好的，Rust在这种地方可能显得有些繁琐了，有些时候要大量的`as`看得人头皮发麻，但这是一种 trade-off。在方便的应用场景之外发生的隐式转换是难以排查的错误。`i32`转到`i8` 就不那么惬意了，而整数和`bool`之间的转换也是错误的源泉，为了类型安全多一点繁琐不是一件难以接受的事情，显式优于隐式。

所以来看看C++的显式转换吧，书上说显式转换是危险的，但我觉得隐式转换也很危险：

### static_cast

应该和 Rust 里面的`as`类似，不过能转换`void*`。

### const_cast

去掉 const，类似给对象强制加上 mut，可以看到这简直是玩火，书上举了个函数重载中安全使用的例子。

### reinterpret_cast

不改变内存中的数据，直接改变类型，在 Rust 中是 [`std::mem::transmute`](https://doc.rust-lang.org/beta/std/mem/fn.transmute.html)。

## 初始化

Rust 没有初始化这东西的说法，只能调用构造方法（仅仅是一个返回自身类型的普通方法），或者手动填上 struct 的每一个field。拷贝初始化被用显式调用对象的 `.clone()` 方法来进行。

对C++来说这里面水很深，不严格讲初始化过程中用到了等号的是拷贝初始化，不然就是直接初始化。我自己的理解是，如果想用另一个对象拷贝到新对象的话（也就是希望获得Rust中的 `clone()` 的话）才用拷贝初始化。

~~~c++
vector<int> foobar = {1, 2, 3, 4};
~~~

这里其实语义上是临时创建了一个 `initializer_list` 对象装 `{1, 2, 3, 4}`，然后拷贝到新创建的 vector 里面……这当然有性能损失。

不过这里不用等号也是一样的，用列表初始化来直接初始化也会构造一个 `initializer_list` 对象复制进 vector 里的。

另外就是因为花括号的语义是创建一个临时的对象，所以花括号构造和 `auto` 就不兼容了，直接就推导成 `initializer_list` 类型。

如果用圆括号直接初始化的话，就是调用这些类自己定义的构造函数了，构造函数还能重载……所以千万别把花括号和圆括号搞混了。

还有编译器会合成默认的构造函数，你可以用 `=default` `=delete` 来控制这东西。

搞得那么复杂确实没有什么必要，构造说到底没有什么特别的，就是一些返回自身类型的函数而已，为了省几个字符弄了一堆法则，实在是让人抓狂。

## 相关资料

### 初始化

* [Effective Modern C++ Note 01](https://zhuanlan.zhihu.com/p/21102748) 
