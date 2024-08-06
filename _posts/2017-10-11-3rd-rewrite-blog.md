---
layout: post
title: 第三次重写博客
date: 2017-10-11 06:14:29 +0800
category: dev
summary: 我保证这是最后一次了，最近几年。
typora-root-url: ../
typora-copy-images-to: ../media
image: /media/3rd-overhaul.png
---

因为更换服务器的关系，博客挂了半个月，反正我也没写文章，不是吗？

当然啦，还是用到了大量上一版的代码，不过CSS这次用[SASS](http://sass-lang.com)重写了，最大的改变除了样式以外就是加入了汉字标准格式的支持，下划线也用Javascript绘制。

对了博客的代码现在[可以在GitHub找到](https://github.com/tioover/ioover-blog)了。我希望自己能勤奋地迭代，给Blog加上夜间模式、文章加上直排选项什么的就不错。

打算找点友链了。

## [汉字标准格式](https://hanzi.pro)

虽然库提供了CDN直接引用文件的选项，但是因为SASS可选项非常多，自己的SASS文件引用编译才能发挥它的最大效果。

这里有几个坑，比如说Jekyll因为忽略下划线开头的文件，所以无法编译；再比如说遇到了一个编译错误，只能fork了修改。

有些选项还是比较重要的，请参阅官方的API页面，[这是SASS](https://hanzi.pro/manual/sass-api)，[这是JS](https://hanzi.pro/manual/js-api)。

为了兼顾直排，JS也禁用了标点悬挂和挤压。



## [SmartUnderline](https://github.com/CloudflareApps/SmartUnderline)

![pretty-underline](/media/pretty-underline.png)

能够很好处理 [jgpq](http://ioover.net/) 这类字母下部和下划线交互的库，浏览器原生支持只有Safari，导入JS以后需要一行 `SmartUnderline.init();`来启用。

GitHub类似仓库排名第一的[Underline.js](http://underlinejs.org)，很遗憾[没有太准备好实际使用](https://github.com/wentin/underlineJS/issues/32#issuecomment-151965743)。

实际上这个对直排也不太好处理。有可能禁用。

## 关于直排

我不觉得直排优于竖排，但是一种陌生感是很棒的。看漫画的时候大家也比较喜欢直排，这是因为漫画是竖直的，水平的空间比较紧张，而且本身翻页和格子就是从右到左，说白了也是习惯的力量。

网页的直排，对于很多公式和西文的内容就别想了，但如果全是字的话，可以有的时候尝试一下，如果点个按钮就能在两者间切换就是最好的了。

一个额外的一点是，我觉得直排特别适合手机横屏阅读。

## 关于设计

实际上没什么设计，作为尝试的结果把标题竖直放置了，也不知道讨人喜欢不。

对首页的文章列表，尝试了flex布局，但是因为太整齐了，所以换成了column栏式布局，并且做了点自适应。但是flex确实好用，所以在一些小地方也用到了。

基本剔除了`px`单位，而是用`pt`和`em`、`rem`定义种种大小，这样写自适应的时候只需要更改根节点的字体大小就行了。

一个很注重也要努力的一点就是语义性，我觉得写静态博客这件事还是蛮老派的，所以用老派的方式看待HTML吧，没有CSS和JS完全不影响（除了数学公式）。

<small>我从初中开始写博客，不管发生了什么，我希望能写下去。</small>
