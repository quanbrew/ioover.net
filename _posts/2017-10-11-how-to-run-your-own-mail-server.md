---
layout: post
title: 通过Mailcow拥有自己的邮件服务器
date: 2017-10-11 22:36:59 +0800
category: dev
summary: 折腾，使劲折腾。
typora-root-url: ../
typora-copy-images-to: ../media
image: /media/getmail.png
---

众所周知，希拉里有自己的邮件服务器。这篇文章就是关于自己的邮件服务器的。说这个事倒是有点儿晦气。

## Why

自己架一个邮件服务器的好处大概有这些：

### 无限的邮箱地址

只需要设置一条catch-all的转发记录，你可以给每个网站一个邮箱地址，比如说 alipay@example.com，用久了可以看到到底是哪个网站泄露了你的邮箱，如果一个账号不想用了，或者垃圾邮件太多了，只需要把这个账号的邮箱都丢弃就好了。

### 安全

当然也没那么安全，至少守护你邮件安全的责任由你自己负责。

### 便宜

去买国外的企业邮箱还是要花不少钱的，而且还有一些限制，比如说账号数限制。但是自己架设的话倒是用不了几个钱，国内的话……

### 可以给亲朋好友一个邮箱

但是不推荐这样做，给了别人，哪怕他们没在用，也感觉有维护的责任了……

### Zhuangbility
最重要的是当然是这个啦，而且短小好记，比如说我弄的这个：

![mail](/media/mail.svg){: .right}

加上t就是自己之前常用的ID：tioover，因为不喜欢开头的t所以去掉了注册了这个网站，我也没想到可以这样做。

## Which

不过拥有VPS的话，现在架设邮件服务器还是挺容易的，有不少解决方案。对于这种自己架设什么的事情，除了在[alternativeto.net](https://alternativeto.net)或者[slant](https://slant.co)翻找合适的方案以外，还可以到[reddit的self-hosted](https://www.reddit.com/r/selfhosted/search?q=mail&restrict_sr=on)板块去搜索。

* 自己架设，主要是各种耦合的组件之间不好配置好，然后一些高级的功能不方便管理。
* [Mail-in-a-box](https://mailinabox.email) 比较多人的选择，还有一些类似的。
* [mailcow](https://mailcow.email) 通过docker compose来管理的，*这篇文章的选择*。
* [tvial/docker-mailserver](https://hub.docker.com/r/tvial/docker-mailserver/) docker 的简单方案，系统要求低，功能少，管理困难，但是资源占用少，关掉杀毒软件512MB的内存就能跑，我之前的选择。

之前用[DigitalOcean](https://www.digitalocean.com)（在中国）速度慢不说还贵，切换到别的主机上内存直接翻了一倍。所以最后一个选项pass掉了，然而可叹的是[Vultr](https://www.vultr.com)新用户的邮件端口是被屏蔽的，因为被用来发垃圾邮件。

## How

Mailcow 的文档已经有很详细的说明了，只要照着做就可以了。

安装的时候会要求你提供[FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name)，这是`[计算机名].[域名].[域名后缀]`的形式，比如说本服务器服务器名叫serval，那就是`serval.ioover.net`，推荐前面的部分填mail之类的，然后用这个FQDN，去主机商那里做[反向域名解析](https://en.wikipedia.org/wiki/Reverse_DNS_lookup)。

一些重要的DNS设置照着做，安装完了可以设置[DKIM](https://zh.wikipedia.org/wiki/DKIM)，然后再去修改DNS启用。

值得注意的是在生成的配置文件必须把CLAMD关了，不然多少内存都不够，平常大概会用掉500多MB的内存，而且用自架服务器的人还是不太需要杀毒软件的吧。

安装完了以后就可以看到萌萌的登录页面了：

![mailcow-login](/media/mailcow-login.png)

底下的SOGo是在线的邮件客户端，如果懒的配置客户端的时候可以用。

直接登录进去就是完善的管理页面，多用户，多域名，可以查看日志，添加黑名单等等，比如说这个页面就是生成DKIM的：

![mailcow-admin-dkim](/media/mailcow-admin-dkim.png)

右上角切换到邮箱管理。

![mailcow-enter-mailbox](/media/mailcow-enter-mailbox.png)

这里可以管理每个域名和邮箱，比如说这个邮箱aliase就可以转发所有@ioover后缀的邮件。

![mailcow-manage-mail-aliases](/media/mailcow-manage-mail-aliases.png)

这是很完善的多用户系统，每个用户也能登陆后台进行用户级别的设置，除了更改密码以外，每个用户可以创建临时的邮箱aliases，管理垃圾邮件黑白名单，等等。

![mailcow-temp-aliases](/media/mailcow-temp-aliases.png)

架设好了以后就去[发个邮件测试一下](https://www.mail-tester.com)，我这里配置好了就是10分满分。

![mail-tester-10](/media/mail-tester-10.png)

如果一些地方出错的话发给GMail什么的就会被放进垃圾邮件，别怕，设置好了就行的，不会加入黑名单的。

剩下的资源可以[架个PHP网站](https://rpg.eggfan.org)、<ruby>科学上网<rt>fan qiang</rt></ruby>什么的，主力机建议还是另外开一个，比如说本域名的邮件服务器就是解析到别的服务器的。
