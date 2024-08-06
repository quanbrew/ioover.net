---
layout: post
title: 第四次重写博客
date: 2018-07-04 15:14:20 +0800
category: dev
summary: 又，又，又，又重写了！本篇文章是一些细节碎碎念。
typora-root-url: ../
typora-copy-images-to: ../media
image: /media/ioover.net_2018-07-04.png
toc: true
---

本站点重写的历史：

1. [总把新桃换旧符](https://ioover.net/dev/blog-overhaul/)
2. [再次重新设计](https://ioover.net/dev/blog-overhaul-again/)
3. [第三次重写博客](https://ioover.net/dev/3rd-rewrite-blog/)
4. 就是本文啦

忘备份网站源代码，找到的最新的源码是今年三月的。所以有些改动和文章丢失了。随便就能恢复，问题不大，但是以此为契机重写了博客的代码。

上次偷偷说「这是这几年内最后一次重写」。结果并没有 (

## 页面设计

虽然说不断重写，但是我回顾以前的文章，还是能看到不断被继承的脉络。

因为是以文字为主的博客，所以在排版上一直希望做到尽可能好。

整体上来说还是没有多少变化，单栏白底。

我试了很多背景色，包括渐变的。但是发现无论如何都离不开纯白背景。

正文还是妥协用了黑体。电子设备，各方面无衬线更合适一点也支持得好一点。

「汉字标准格式」库很不错。但是我希望有更强的掌控力，所以只拆出需要的一点点代码来用。现在我主要需要那个中西文间自动标记空格的feature，考虑以后拆成一个单独的库。

在前几篇文章**纠结**过的下划线（<ins>你马上会看到有多纠结</ins>），也有[自己专门的CSS属性](https://developer.mozilla.org/en-US/docs/Web/CSS/text-decoration-skip)了，虽然只有很少浏览器支持。<s>而现在本站的下划线也主要是用一个渐变的background来绘制，而不是浏览器自带的下划线（underline），这样能方便定制样式。</s><del>至少Chrome似乎还不能定义下划线的颜色，更不用说位置了。</del><ins>好像我搞错了，<s>现在已经主要用浏览器自带的下划线了。</s></ins><ins><s>结果链接又用回渐变背景色的方案了</s>。</ins><ins>现在用了新方法。</ins>

响应式布局应该算基本了（试试看缩小浏览器窗口的宽度）。因为是单栏布局，且没有用绝对单位，所以是自然而然的事情。

相信你一定注意到了某些竖排文本。

<aside class="gamemaster">
<p>探險者猛一回頭，豐富的經驗告訴他好像有什麼東西在試圖「指涉」他。</p>
</aside>

这被我称为*Game Master 文本*，用来模拟TRPG中主持人的称述。其实是一种和正文关系不大的装饰性文本。我之后会写一些关于TRPG的文章 XD

这是我最喜欢的一部分，这是不是让本站或多或少有点与众不同呢？中二是我的美学！


## 前端

写了五天多前端，感觉自己…

本来上次重写博客就快写吐了。

### CSS

越用越喜欢SCSS，如果没这东西光用CSS来写东西简直是灾难。因为还是想写出漂亮的页面，所以CSS重写了两次。昨天字面意义上写到吐了，今天上午改掉了一些细节才勉强算一个正式版。

### JavaScript
这次完全搞掉了NPM。再见 `package.json`，再见 `node_modules`。

也没有评论，也没有跟踪代码。不会记录来访者的身份，觉得太麻烦了，也没必要。

本站可以说是属于上个世纪的静态内容站点。虽然还必须要求最新最酷最炫的浏览器，但是没有开JavaScript的话也不会影响阅读。（最大的问题是 $$\LaTeX$$ 会变成源码）

脚本可以用来按需加载JavaScript：比如说网页上没有数学块就不加载MathJax；没有代码块就不加载代码高亮。

这个想法是好的，但是遇到了个问题，iOS上的Safari的JavaScript对类似于形如 `.querySelectorAll('script[type*="foobar"]')` 这样的查询似乎不兼容（没有仔细调查）。而且按需加载需要等待页面载入完才能判断，并没有多少性能提升，还有可能反而拖慢载入。作罢。


### HTML

用了[这个生成器](https://realfavicongenerator.net/)来用Logo生成图标。非常满意，而且还能让我的网站加到主屏幕上：[YouTube 视频](https://www.youtube.com/watch?v=A1lvkvlv_l8)

<aside>
<p>顺带一提Logo当然重绘了。</p>
</aside>

## 后台

我觉得很好的一个改变是，主页的日志和友情链接是用YAML生成的：

~~~yaml
logs:
  - text: 再次几乎重写了博客。
    date: 2018-07-01
  - text: 稍微修整一下博客，删掉了Google Analytics和Disqus评论。
    date: 2018-01-12
  - text: 开始记日记了
    date: 2018-01-04
  - text: 2018年一切都会好的！
~~~

模板读取：

~~~html
<ol class="log-list">
{% raw %}{% for log in page.logs %}
  <li><span class="log-text">{{log.text}}</span>{%if log.date%}<time datetime="{{log.date}}">{{log.date | date: "%m/%d"}}</time>{%endif%}</li>
{% endfor %}{% endraw %}
</ol>
~~~
很多结构化的页面应该用这种方式处理而不是直接写。

后台，用到了 Docker…因为Jekyll有Ruby这一堆依赖，用Docker管理也没什么毛病。

尝试了一下文章和网站的代码分开成两个仓库。优点很明显，但好像和Docker冲突了，因为需要符号链接。刚打下这段话了以后，我想到了一个新的解决方法，待会去看看。

## 今后的工作

最主要当然是写更多的文章啦，在文章里我可以自由地调戏来访的<ruby>探险者<rp>（</rp><rt>你</rt><rp>）</rp></ruby>。

![teletubbies](/media/teletubbies.jpg)


<aside class="gamemaster">
<p>探險者回過頭後，發現一羣天線寶寶出現在背後，在陰影中發出天真無邪的笑聲。</p>
<p>「嗚啊啊啊——」探險者撒開丫子跑了起來。</p>
</aside>

笑）

（喂喂喂

所以，看看<ruby>探险者<rp>（</rp><rt>你</rt><rp>）</rp></ruby>到底会有什么样的大冒险吧。

会加一点可爱的图片，把文章中盗来的图替换成我自己画的。比如这就是我画的，用[MagicaVoxel](https://ephtracy.github.io/)。

![我画的](/media/getmail.png)

体素画图还是很有意思的 XD

