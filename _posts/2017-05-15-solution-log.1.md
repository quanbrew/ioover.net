---
layout: post
title: 解题日志 1
date: 2017-05-15 13:05:11 +0800
category: learn
summary: 简单纪录碰到的问题以及解决思路
typora-root-url: ../
typora-copy-images-to: ../media
---

既然大费周章又一次重写了Blog，那就得用呀。

这几篇文章用来记录遇到的各种问题以及解决思路。

## 矩阵清零

给一个矩阵，将0处的行列清零，要求$$O(1)$$空间复杂度[^1]：

[^1]: 题目上先说「原地」然后又解释原地是$$O(1)$$空间复杂度，实际上原地不一定$$O(1)$$，比如说快排就是原地的。

$$
\begin{bmatrix}
x & 0 & x & x\\
x & x & x & 0\\
x & x & x & x\\
\end{bmatrix}
\rightarrow
\begin{bmatrix}
0 & 0 & 0 & 0\\
0 & 0 & 0 & 0\\
x & 0 & x & 0\\
\end{bmatrix}
$$

当时没想出来，实际上很简单，做到$$O(1)$$的关键之处就是在矩阵内部记录哪些行列需要清零。

先遍历每行，找到一个没有0元素的行，然后对每列如法炮制，找到无0行a和无0列b（如果任一找不到那就说明整个矩阵为**0**）。将这两个作为记录向量。

然后再次遍历整个矩阵，跳过a,b，对遇到的每个 $$ 0_{i,j} $$，将 $$a_j,b_i$$ 处的元素清零。


$$
\begin{bmatrix}
x & 0 & x & x\\
x & x & x & 0\\
x & x & x & x\\
\end{bmatrix}
\rightarrow
\begin{bmatrix}
\mathbf{0} & 0 & x & x\\
\mathbf{0} & x & x & 0\\
\mathbf{x} & \mathbf{0} & \mathbf{x} & \mathbf{0}\\
\end{bmatrix}
$$


于是最后a中每个为0的元素就对应着需要清零的列，而b对应每个要清零的行。没有申请新的空间。

## [Data Types à la Carte](https://www.codewars.com/kata/data-types-a-la-carte)

这里介绍了一种不修改原有代码扩展程序的方法。

这题很坑的是，现在有Bug ，所有用例通过了以后，因为 `stderr` 有警告所以过不了。

不过还是非常有教育意义的，作为一个 Hasekll 新手，花了很长时间做了以后感觉学到了很多，感觉就是类型的完形填空。[解答在这里](https://gist.github.com/tioover/ef739f6e60fe926d0864b09aa1453d0c)。

这里写一点注解。

~~~haskell
newtype Expr f = In (f (Expr f))
~~~

这是重要的类型，In为类型构造器，所储存的类型是 `f (Expr f)` ，有点递归的感觉。这里隐含的是f是一个 `* -> *` 的类型构造器，f的类型参数必须是 `Expr f` 自身。

<aside>

**UPDATE**: 这其实是函子不动点 Fix，稍微改造一下就是 Free Monad。

</aside>

比如说 `Expr Add`

~~~haskell
In (x) :: Expr Add
x :: Add (Expr Add)
x = Add a a
a = Lit 42 :: Lit (Expr Add)
~~~

作为终端的 `Lit a` 内部永远是 `Int` 但是有一个类型参数 `a` 作为一个泛用的marker用来匹配所在表达式的类型。

`Lit`, `Add` 这些类型都是Functor，也就是说可以 `fmap` ，因为 `Lit` 内部永远是 Int，转换的时候重新构造一下就好了：

~~~haskell
instance Functor Lit where
  fmap f (Lit x) = Lit x
~~~

而在解释前，`Add` 这些类型的参数往往是 `(f :+: g)`，这是 [Coproduct](https://en.wikipedia.org/wiki/Coproduct) 一个范畴论的概念，不过其实没那么可怕：

~~~haskell
data (f :+: g) e = Inl (f e) | Inr (g e)
~~~

从 `f e`  可以看到 `f :: * -> *` 是一个 Functor，g 自然也如此，`(f :+: g) e :: *` 考虑类型层面上的 curry 化，`(f :+: g)` 就也是一个Functor ，在这里 `:+:` 连接两个Functor，返回一个新的Functor，这两个Functor都可以转成这个新的Functor。

之后遇到：

~~~haskell
foldExpr :: Functor f => (f a -> a) -> Expr f -> a
~~~

这个函数的填空难住了我好久，其实是上面的概念不清晰的缘故。

`Expr f` 里面可以取出 `f (Expr f)` ，但需要的是 `f a`，怎么才能把 `f (Expr f)` 转换成 `f a` 呢？找不到办法。 

实际上走到这步已经离解决很近了，我陷入胡同是因为忽视了这个函数自身，因为在我的理解当中递归是要写终止条件的，但是惰性求值的Haskell其实不一定。

经人提醒我才发现，既然 `f (Expr f)` 中 `f` 是Functor，而Functor只有 `fmap` 可以利用，利用 `fmap` 就可以把内部的 `Expr f` 转成 `a`，那这里只有 `foldExpr` 自身满足类型约束，这是唯一解。

~~~haskell
foldExpr f (In e) = f $ fmap (foldExpr f) e
~~~

填空了，编译通过以后再回过头来解释，这也是Haskell的奇特之处吧。

上面提到了终端的 `Lit a` 其实不会 care `a` 是什么的，传进来的 `f` 也不会用到，所以这里不断递归，递归到 `Lit a` 的话就直接转换不会触发无穷递归。

后面这道题给了一个表达式表示，虽然你写出来了，但是编程非常麻烦：

~~~haskell
pain :: Expr (Lit :+: Add)
pain = In (Inr (Add (In (Inl (Lit 5))) (In (Inl (Lit 6)))))
~~~

这个虽然作为一个麻烦的例子，但是在前面还是为我的理解提供了很大的帮助的。

这里痛苦之处主要是在于把一个 Functor 根据上下文提升到 Coproduct Functor，如果能让编译器根据类型推导自动帮你提升就行了：

~~~haskell
class (Functor sub, Functor sup) => sub :<: sup where
  inj :: sub a -> sup a
~~~

这里的 `:<:` 是 $$:\prec:$$ ，意思是sub是sup的子类型。

根据上下文 `Add` 就会被提升成 `(Add :+: Int)` 。具体转换过程挺简单的略过不提，最后包装出了一个函数：

~~~haskell
inject :: (g :<: f) => g (Expr f) -> Expr f
inject x = In (inj x)
~~~

类型签名才是精髓。

g属于f，也就是说f是 $$g:\prec:h$$ 或者 $$h :\prec: g$$ ，两者等价的。

传进来的g是用户书写的原本的函子。而 `f` 是编译器推导出来的，此处表达式所需要的 Coproduce 函子。`inj` 提升了以后就变成 `f (Expr f)` ，塞进 `In` 就变成一个表达式了。

### 感想

做这题才有点在写Haskell的感觉了，没想到函子那么基础的结构也能有那么大的power，谢谢[这里](https://zhuanlan.zhihu.com/p/20528665)莎莎提供的[习题列表](https://www.codewars.com/collections/haskell-3)。

感觉Codewars更注重语言本身的训练。不过这题的Bug一直没能修有点难受。（后来修了）

-----------

写得太多了花费了不少时间，实际上解题日志这种的话应该比较简略地写，大致的思路就行了，就当开个头吧。
