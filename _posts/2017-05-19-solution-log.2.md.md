---
layout: post
title: 解题日志 2
date: 2017-05-19 09:47:36 +0800
category: learn
summary: 入门一下动态规划
typora-root-url: ../
typora-copy-images-to: ../media
---

这次主要[入门一下动态规划](https://leetcode.com/tag/dynamic-programming/)。

## [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/#/description)

最简单的类型，因为自己对动态规划一窍不通所以学一下。

> You are climbing a stair case. It takes *n* steps to reach to the top.
>
> Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?

$$
 \begin{aligned}
f(1) &= 1\\
f(0) &= 1\\
f(n) &= f(n-1)+f(n-2)
\end{aligned}
$$

## [Unique Binary Search Trees](https://leetcode.com/problems/unique-binary-search-trees/#/description)

求二叉搜索树可能的种数。


$$
 \begin{aligned}
f(1) &= 1\\
f(0) &= 1\\
f(2) &= 2\\
f(n) &= \sum_{i=1}^{n}{f(i-1) \cdot f(n-i)}
\end{aligned}
$$



这时候发现做算法题的时候还是不需要开 `vector`，初始化什么的很麻烦诶，`array` 一个大数组就够了。


## [Maximum Subarray](https://leetcode.com/problems/out-of-boundary-paths/)

《编程珠玑》8.4 节上有。

这是连续子向量最大和问题，所以用扫描线算法。维护*历史最大*向量和 以及 *以当前元素为结尾*的**正**向量和，并且不断比较更新。

仔细想想，这确实也是动态规划。

唯一要注意的是，编程珠玑里面记载的代码，似乎遗漏了全是负数序列的情况。所以如果结果为 0，要返回 `*max_element(nums.begin(), nums.end())`。

-----------

这篇就到这里吧，都太简单了，熟悉一下概念，晚上做难一点的
