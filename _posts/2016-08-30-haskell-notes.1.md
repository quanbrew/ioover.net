---
title: Haskell 学习笔记 (一)
layout: post
category: learn
toc: true
summary: 非常入门级的笔记。有错请指出哦。
---

废了那么长时间，也该学拖延了两年的 Haskell 了。非常入门级的笔记。教材选择的是[阅千人而惜知己](http://weibo.com/u/1914643755)的《[Haskell 函数式编程λ门](https://book.douban.com/subject/25843224/)》，以及《[Haskell 趣学指南](https://www.gitbook.com/book/mno2/learnyouahaskell-zh)》搭配着看，还有一些知乎上的文章用来参考。

《Haskell 函数式编程入门》这书需要[勘误表](https://github.com/HaskellZhangSong/Introduction_to_Haskell)，我觉得内容本身还是非常不错的。初学者的话可能看《[Haskell 趣学指南](https://www.gitbook.com/book/mno2/learnyouahaskell-zh)》更平易近人一些。还有大名鼎鼎的《[Real World Haskell](https://rwh.readthedocs.io/en/latest/)》。
<!--more-->

## 环境搭建

这里主要参考的是邵喵的《[不动点高校迎新会](https://zhuanlan.zhihu.com/p/20296136?refer=fixpoint-high-school)》这篇文章。不过注意的是，构筑工具最好用 stack，而且[国内已经有镜像了](https://mirror.tuna.tsinghua.edu.cn/help/hackage/)。如果遇到什么问题的话[可以看这个讨论](https://github.com/CNMDR3G/CNMDR3G/issues/36)。

就像文章里说的，Atom 搭配 ide-haskell 就很好，详细的配置可以参考《[打造令人愉悦的 Haskell 开发环境](http://www.jianshu.com/p/605042ea7c16)》。

### 字体

还有一个小准备就是可以安装特殊的字体文件，Haskell 里面有很多特殊的符号，如果用了专门的字体看起来会很舒心，比如说 [Hasklig](https://github.com/i-tu/Hasklig) 或者 be5 大大做的 [Iosevka](https://be5invis.github.io/Iosevka/)，以及配套的全 Unicode 等宽字体 [Inziu](https://be5invis.github.io/Iosevka/inziu.html)。

因为这些字体用到了 OpenType 的连笔字特性，Atom 里面默认是关闭的，所以要在 Atom 的样式表里面加入

```css
atom-text-editor {
  text-rendering: optimizeLegibility;

  /* 仅当用 Iosevka / Inziu 时需要。 */
  -webkit-font-feature-settings: "XPTL";
}
```

## `foldr` 和 `foldl`

看《趣学指南》的时候，把 `foldr` 和 `foldl` 说得有点简略了，说 `foldr` 是从列表的右边开始折叠的，`foldl` 是从左边。但是这就让人搞不懂为什么，对一个无穷列表 fold 的同时产生一个新的列表，`foldl` 会陷入无穷循环而 `foldr` 不会。

```haskell
> take 10 $ foldr (\x z -> x+1:z) [] [1..]
[2,3,4,5,6,7,8,9,10,11]

> take 10 $ foldl (\z x -> x+1:z) [] [1..]
...
```

如果从列表的右边开始的话，对于 `foldr` 访问无穷列表最右端的元素是永远访问不到的，反而应该陷入无穷循环，而 foldl 因为从左边开始，所以完全可以随时截断。

实际上是因为 Haskell 的惰性求值的关系，`foldl` 是从左到右尾递归的，不需要中间展开栈空间，但是代价就是仅当递归结束以后才会返回一个值，对于无穷 list 的情况，不能返回一个惰性的 list。

而 `foldr` 不是，引用上了 `foldr` 并返回一个 list 的时候，实际上还没真正开始折叠就返回了一个惰性的 list，当去 `take` 的时候才会执行里面的代码。`foldr` 的时候，返回的 list 的头部变成了 x+1 但余部还没进行求值。

当然，`foldl`确实是从左到右折叠的，而 `foldr` 确实是惰性地从*被截断处*的右端到左端折叠的。

这里面还有限制就是你在传进 `foldr` 的函数中，只能不能获取余部的值：

```haskell
foo :: Num a => a -> [a] -> [a]
foo v [] = [v]
foo v (x:xs) = v+x:(x:xs)
```

这样的函数

```haskell
> foldr foo [] [1..10]
[55,54,52,49,45,40,34,27,19,10]
> foldr foo [] [1..]
...
```

就会陷入无限循环了。因为你要求了后面的值，所以就惰性不起来了，必须算完。

[具体推荐这篇](https://www.zhihu.com/question/37817937/answer/73958515)，特别是里面两张图非常有助于理解。

## 类型的 kind


类型的 kind 语法类似函数，实际上也类似函数：

```haskell
* -> * -> *
a -> a -> a
```

对于函数来说，可以看作需要多少个值，才能确定一个最终的、非函数的值。

而对于 kind 来说，就是需要多少个类型，才能确定一个最终的类型。所以就像函数签名一样，kind 也在描述所需的类型参数的结构。

而高阶 kind，正如高阶函数需要别的函数来确定最终值一样，高阶 kind 也是需要别的多态类型（也就是说还没被确定下来的类型，kind 不是 \*）来确定自己的类型，高阶函数的参数可以替换所以很灵活，高阶 kind 的类型构造器也可以替换，更是灵活，这也是后面很多 Type class 能被定义出来的基础。

----------

今天要去拔牙了 QAQ
