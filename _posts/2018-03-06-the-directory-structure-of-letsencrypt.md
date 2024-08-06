---
layout: post
title: Let's Encrypt 的目录和权限结构
date: 2018-03-06 00:47:22 +0800
category: dev
summary: 这是一篇短纪录（为另外一篇文章打个底）
typora-root-url: ../
typora-copy-images-to: ../media
---

这是一篇短纪录（为另外一篇文章打个底），目录结构是Let's Encrypt自己的获取工具certbot建立的，默认的设置有点奇怪，但还是能用，为了不麻烦就不改了。

```bash
$ ls /etc/letsencrypt -lah
total 56K
drwxr-xr-x   9 root root 4.0K Mar  6 00:14 .
drwxr-xr-x 107 root root 4.0K Mar  1 22:42 ..
drwx------   5 root root 4.0K Mar  1 19:11 archive
drwx------   5 root root 4.0K Mar  1 19:11 live
...
```

其他的都不重要，重要的是`live` 和 `archive`。这两个文件夹都是 `700` 的，用文件夹权限来进行权限控制。

`live` 是一般在配置里指定的证书路径，实际上 `live` 里面装的是指向 `archive` 的软链接。所以拷出证书的时候不能直接复制 live 里面的东西，会复制到软链接的。可以用 `cat` 或者 `cp -L`。

~~~bash
/etc/letsencrypt/live
├── download.ioover.net
│   ├── cert.pem -> ../../archive/download.ioover.net/cert1.pem
│   ├── chain.pem -> ../../archive/download.ioover.net/chain1.pem
│   ├── fullchain.pem -> ../../archive/download.ioover.net/fullchain1.pem
│   ├── privkey.pem -> ../../archive/download.ioover.net/privkey1.pem
│   └── README
~~~

`archive` 里是实际的证书文件。

~~~bash
-rw-r--r-- 1 root root 1.9K Mar  1 00:38 cert1.pem
-rw-r--r-- 1 root root 1.7K Mar  1 00:38 chain1.pem
-rw-r--r-- 1 root root 3.5K Mar  1 00:38 fullchain1.pem
-rw-r--r-- 1 root root 1.7K Mar  1 00:38 privkey1.pem
~~~

注意访问权限是目录权限控制的，本身里面的**证书文件是所有人都有读权限的**，包括私钥。小心隐含的安全问题，如果我把证书文件**硬链接**到外部，所有人都可以访问这个证书文件。

`archive` 最新申请的证书是文件名中编号最大的，每次续签的时候就是申请新证书然后把符号链接指过去。
