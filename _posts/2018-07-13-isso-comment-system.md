---
layout: post
title: 让isso给你的静态网站加上评论
date: 2018-07-13 13:42:59 +0800
category: dev
summary: 如何给静态网站加评论？我选择了isso
typora-root-url: ../
typora-copy-images-to: ../media
---

如何给静态网站加评论？常见的方法是[Disqus](https://disqus.com/)。但是Disqus会收集用户数据、不开源、不属于我，打开控制台会发现Disqus留下不少错误信息。于是我最终删除了Disqus，顺带还有Google Analytics。

经过一番搜索我找到了[isso](https://posativ.org/isso/)。

![Wynaut](/media/Wynaut.png){: .right}

* 轻量级
* Python写成
* 配置简单
* 支持Markdown
* 支持中文
* 整洁干净
* 可以完全匿名
* 可以点赞点踩
* 编辑自己说的话
* 支持邮件通知
* 可以成串（thread）回复，也就是楼中楼
* isso是宝可梦里面的「小果然」的德文名字

但也有缺点：

* 配置相对简单，但是非专业人士还是不太好装上去的
* 默认不支持Gravatar，因为[隐私方面的问题](https://posativ.org/isso/faq/)（会泄漏邮件地址）。但我觉得不需要这么严格，毕竟可以选择是否留下电子邮件。我试图在这方面看看有没有什么解决方案。isso的GitHub仓库里面有对Gravatar支持的分支。
* 如果一个页面没有评论，会在控制台留下一次404失败请求。强迫症会有点难受。

我是用[Docker部署](https://hub.docker.com/r/wonderfall/isso/)的。不过isso很轻量，也就依赖Sqlite和Python什么的，直接部署也没什么不好。