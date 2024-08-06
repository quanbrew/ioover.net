---
layout: post
title:  再次重新设计
date: 2017-05-15 00:00:06 +0800
category: dev
summary: 与其说强迫症不如说是逃避现实，又重写了一遍Blog。
typora-root-url: ../
typora-copy-images-to: ../media
---

现在明明是忙都忙不过来的时候我还花了好几天的时间折腾网站。嘛，这个想法很早就有了，算是了却一桩心事吧。<!--more-->

![ioover.net-screenshot](/media/ioover.net-screenshot.png)

**TL;DR**: 需要注意的，推荐安装「[思源宋体](https://source.typekit.com/source-han-serif/cn/)」来获得正常的阅读体验。用到的技术有Webpack、SVG Symbol。

## 造轮子的尝试

用着jekyll还是有一些不顺心的地方，在这驱动下我想尝试自己写一个网站生成器，自己造轮子如果和原本的轮子长得太像那就不好，仿jekyll还不如，在我的设想中主要是这样的。

1. 不需要写元信息（meta），发文章还需要写meta实在有点打击我写文章的积极性，可以自动从文件创建获取发布时间，从文件所处的文件夹获取分类。从文章的 `<h1>` 获取标题。这样每次需要写文章直接开写就行了。
2. 自动解析并转换引用的相对路径。和上面是同一个思路，面向文档写文章而不是面向文档生成器。文章内引用的图片等相对路径在编译的时候会自动转成url，而不需要每次贴图的时候把图片放到Jekyll目录下面的图片文件夹，然后在编辑器上写个本地看不到的死链。
3. 因为是自己的轮子所以要搞小修改挺方便，比如说生成更合理的HTML标签、为每个页面生成字体文件什么的，再比如说Jinja2 模板也更和蔼可亲，我又不会Ruby （;￣O￣）

所以做出来了吗？做是做出来了，写了个小脚本实现了初步的转换，但就在这里呆住了。

不写meta想法是好的，但是文件系统上文件创建的时间很不靠谱，当初我的想法是用git追踪时间，这也挺好，直到我试图搬运以前的文章，发现git修改某一个文件的创建时间非常麻烦…我试图通过数据库或者文件来记录时间，但最后意识到还不如就写在头部呢。

重新看看Jekyll，（1）的问题其实是伪问题，我写了个Python脚本来创建一个文章的模板，自动打开[Typora](https://typora.io/)。

（2）的问题确实不好解决，直到我发现Typora已经为图片做了不少工作了，在meta处加上：

~~~yaml
typora-root-url: ../
typora-copy-images-to: ../media
~~~

第一行是显示图片的根目录，第二行是copy图片进文档的时候自动复制一份到media文件夹。

（3）只是心情问题了，学一点Ruby写一下扩展也不是难事。

## 回到Jekyll

没有了自己造轮子的理由，就重新看看Jekyll，社区非常大，还是比较方便的。

### 写一个脚本

脚本我放在 [Gist](https://gist.github.com/tioover/6d11f181ff58af2a95ebd5d3097a91c1) 了，[Jekyll本身也有](https://github.com/jekyll/jekyll-compose)，但是感觉无法满足需求。

尤其是现在改用bundler管理依赖以后都需要接一长串 `bundle exec jekyll ...` 非常麻烦，而且我希望利用前端工具链来进行构筑脚本文件，结果这又成了大坑，后面会提到。

### 主题

所以用Jekyll默认的[minima](https://github.com/jekyll/minima)重新开发吧。我其实给minima提交过一个[PR](https://github.com/jekyll/minima/pull/73)，主要是为了演示可行性不指望合并，里面用到了比较时髦的SVG Symol，将一堆小图标合成一个svg文件。这次总算用上了。

参考了之前的代码，还有别人的网站[^1]什么的总归搞出来了。花了大量的时间。

[^1]: 比如说[这个](https://banana.moe/posts/2016-12-02-serif-cjk-font-in-web)，[这个](http://typeof.net/)


结果来看还是之前的风格。希望以后不要再这样重写了，慢慢添砖加瓦就行了。

#### 字体和排版

没时间做[思源宋体](https://source.typekit.com/source-han-serif/cn/)的webfont了，以后可能会试试，所以为了最佳阅读体验请务必下载思源宋体。

另外就是用了一个脚本使得中文和英文间自动会有空格了，但这脚本差强人意，真希望我能改进一下。

最后就是如果把鼠标放在标题上会有标题的链接。整合这些脚本的时候想要用一下现代前端的构筑工具，就耗费了不少时光。

## 痛苦的前端构筑

不知道是我没有系统训练还是怎么的，玲琅满目的前端构筑工具把我搞糊涂了，试了流行的[rollup](https://github.com/rollup/rollup)，[gulp](http://gulpjs.com/)什么的都也不能让我轻松地把脚本和依赖打包到一起。

然后又看了看相关的文章还是没能搞明白，都要绝望了。最后尝试了[Webpack](https://webpack.github.io/)，一直都知道这东西，只是有人不喜欢它所以忽略了。但[了解了以后](http://zhaoda.net/webpack-handbook/index.html)可以说是正合我意了，配置方便，一用就行。只是把CSS也给打包成JS不符合我的审美，不过也不是必须的。

## 部署

之前是用git hook，每次push以后服务器运行脚本，蛮复杂的，而且在服务器端还要维护一个Jekyll环境，现在就试试单纯rsync，挺好用的。
