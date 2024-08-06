---
title: 总把新桃换旧符
layout: post
category: dev
toc: true
---

搬到了新站以后，虽然凑合用着，但是慢慢还是对自己网站的各种细节不太满意。于是开始大修，这一篇就作为笔记。<!--more-->

一开始我只打算花两天时间来弄，因为也就是一个只有几篇文章的静态网站，最后花了两个星期……当然也是我拖延和反复的原因。

现在因为我调试产生的垃圾信息，评论全没了，不过以前的评论我都导出了，有空整理一下 XML 导入又是一条好汉。

## Server

换了个机房，因为主机里没什么东西就换了重来。

配置 Nginx 的 Let's Encrypt 参考的是[这篇文章](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-14-04)，然后[通过 git hook 在接收到 pull 了以后自动部署](https://zhuanlan.zhihu.com/p/19757507)，为此专门创建了一个无权限的用户来管理这个网站。


## HTML

本来打算从 HTML 开始重写的，HTML 花了两天时间写好。

主要是想要纯语义化，HTML 中没有非文档本身的内容，也就是说除了 `class` 和 `id` 属性就不会添加任何与样式或者脚本相关的东西了。

这一步主要参考的是 MDN，里面关于最新 HTML 5 的内容是很新的。

然后由图标注意到了 [SVG Symbol](https://css-tricks.com/svg-symbol-good-choice-icons/)，配合上 `<use>` 看起来完全没有用 font icon 的理由。虽然现在最终的成品根本没有用到…

又发现了[语义化的 Microdata](http://lepture.com/zh/2015/fe-microdata)，这东西用于机器解析网页中的内容。还有[提升 Accessibility 的](http://lepture.com/zh/2015/fe-aria-label) `aria-label`。

所以现在 HTML 学问也不浅了呢。

## CSS

就是在 CSS 这里崩溃的，想要从头写 CSS 对我来说挺痛苦的。

中间略去不提，最后还是决定在原模板上修改，丢弃自己一直在写的全新模板了。

不过修改的地方很多，因为也就一个小网站，希望别人阅读的时候能舒服，所以专注于排版。

### 下划线

之前就看了一篇文章，说有下划线的时候，一些字母的下延部分和下划线叠在一起很难看，[Medium 的前端精益求精解决了这个问题](https://medium.design/crafting-link-underlines-on-medium-7c03a9274f9#.fms4y4m24)。

我这里也按照文章给出的方法搞了个完美下划线：

*the fox jumps over the lazy dog.*

重叠多个一像素的阴影，然后用背景渐变画下划线，就是这样的思路。

```scss
$underline-color: $gray-2;
$underline-width: 1px;
$underline-offset: 0px;
@mixin underline($color: $underline-color, $weight: $underline-width, $offset: $underline-offset) {
  text-decoration: none;
  background-image: linear-gradient(to top, transparent, transparent $offset, $color $offset, $color ($offset + $weight), transparent ($offset + $weight));
  text-shadow: -1px -1px 0 $body-bg, 1px -1px 0 $body-bg, -1px 1px 0 $body-bg, 1px 1px $body-bg;
}

@mixin clear-underline {
  background: none;
  text-shadow: none;
}
```



### 字体

字体当然是重中之重啦。

主要是觉得全世界都在用黑体，macOS 的宋体也不难看，而英文的衬线体又那么好看，这里用宋体做正文字体不是挺好？

买了「[方正博雅宋](http://shop.foundertype.com/index.php/FontInfo/index.html?id=249)」的个人授权，本来想压缩做成 webfont 的，仔细看方正的协议竟然不允许，虽然可以照用但心里总归不爽，所以只是写在了 CSS 里，没有嵌入中文字体。

但是问题来了，macOS 还好，Windows 就比较难看了，有默认字体本身的原因还有渲染的原因，为此还和一个人闹翻了互相拉黑。<del>不过吵架中我的一个收获就是 Windows 楷体其实还不错，在大字号的情况下做正文字体也不是不适合，所以安排了回退，正文字体先宋体后楷体。</del>

最后还是算了不用楷体了，难看就难看吧，一致性最重要。另外感觉现在中文 Webfont 嵌入还是大坑。

*Update* 刚刚又折腾半天，还是没能成功用[字蛛](https://github.com/aui/font-spider)来压缩掉「[文鼎报宋](http://www.arphic.com.tw/zh-tw/support/index#download/4)」，又非常不想用文鼎提供的云字体服务，不是自己服务器、要钱（虽然能试用）、有 PV 限制，最关键是速度不怎么样。

心好累，不想管字体了，Windows 什么的如果看到微软雅黑的话推荐戳一下[文鼎报宋](http://www.arphic.com.tw/uploads/Download/font/gbsn00lp.zip)下载一下，这是非商业免费授权的。

----------

英文字体用了 Google Font 里面的 [Lora](https://fonts.google.com/specimen/Lora)，非常好看又是开源的。

只是突然发现一个问题，很多人都不建议中文用斜体，但是英文肯定是最适合斜体的，怎么混排的时候*让中文不倾斜而 Latin character Italic 呢*。

这里的方法是取消 `<em>` 的斜体样式用 `@font-face` 直接指定字体为斜体：

~~~scss
/* cyrillic */
@font-face {
  font-family: 'EM-CONTENT';
  font-style: italic;
  font-weight: 400;
  src: local('Lora Italic'), local('Lora-Italic'), local('Palatino-Italic'), url(fonts/lora/italic_cyrillic.woff2) format('woff2');
  unicode-range: U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116;
}
/* latin-ext */
@font-face {
  font-family: 'EM-CONTENT';
  font-style: italic;
  font-weight: 400;
  src: local('Lora Italic'), local('Lora-Italic'), local('Palatino-Italic'), url(fonts/lora/italic_latin_ext.woff2) format('woff2');
  unicode-range: U+0100-024F, U+1E00-1EFF, U+20A0-20AB, U+20AD-20CF, U+2C60-2C7F, U+A720-A7FF;
}
/* latin */
@font-face {
  font-family: 'EM-CONTENT';
  font-style: italic;
  font-weight: 400;
  src: local('Lora Italic'), local('Lora-Italic'), local('Palatino-Italic'), url(fonts/lora/italic_latin.woff2) format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2212, U+2215, U+E0FF, U+EFFD, U+F000;
}
~~~

再在字体回退中把 `EM-CONTENT` 排在中文字体的前面。为了和正文区分，用了仿宋作为强调字体，`<blockquote>` 引用的时候也是一样的。

最后是代码字体，用了 [Iosevka](https://be5invis.github.io/Iosevka/)，对于 Haskell 代码，这个字体能连起不少符号：

~~~haskell
class Monad m where
  (>>=) :: m a -> (a -> m b) -> m b -- 称 bind
  return :: a -> m a

echo = getChar >>= putChar

echo' = do 
  char <- getChar
  putChar char
~~~

其他就没什么了，CSS 我也会慢慢改进的。

## Javascript

还没写，现在无脚本。

## Jekyll 

弄的过程中不爽 Jekyll 很久了。

一个问题是模板高级特性比较少，而且生成的 HTML 有一些不一致的地方，特别是代码相关的，用 `~~~` 和 `{% raw %}{% highlight %}{% endraw %}` 生成的 HTML 竟然不一样。而带行号的代码输出更是让我怀疑这些人在想什么。

遇到各种小问题略过不谈，纯静态的话实现标签和分类都不完美。我现在总想自己写个什么来代替 Jekyll，不过这事得放到后头去了。
