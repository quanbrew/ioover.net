---
layout: post
title: Rust 开发环境指北
date: 2017-05-16 22:41:59 +0800
category: dev
summary: 到了现在 Rust 开发环境已经有了比较成熟的解决方案了。
typora-root-url: ../
typora-copy-images-to: ../media
---

有兴趣入门Rust的同学现在不少，一直想写这样一篇文章，但不是我拖延而时机未到，现在今年是社区着力改善工具链和第三方库的年份，相关的成绩挺显著。虽然搭建环境的时候可能会碰到问题，但大致要做的事情已经明了了。

（因为很少在Windows 上开发，本文暂时不会涉及Windows。但基本流程是差不多的。）

## 安装

如果仅仅是想尝鲜体验一下Rust，可以选择用喜爱的软件包管理器安装 `rust` 或者 `rustc`，然后选择一个靠谱的编辑器尝试就行了。

如果尝鲜之后，想系统地学习Rust，并使用方便的开发工具和各式第三方库，需要用官方推荐的方式来安装，在[网站](https://www.rust-lang.org/zh-CN/index.html)有相关内容，为了避免没注意到这里也贴一下：

> ### 使用 `rustup` 管理工具链
>
> Rust 由 [`rustup`](https://github.com/rust-lang-nursery/rustup.rs) 工具来安装和管理。 Rust 有一个 6 周的 [快速发布过程 ](https://github.com/rust-lang/rfcs/blob/master/text/0507-release-channels.md)并且支持 [大量的平台 ](https://forge.rust-lang.org/platform-support.html)，所以任何时候都有很多 Rust 构建可用。 `rustup` 在 Rust 支持的每一个平台上以一致的方式管理这些构建， 并可以从 beta 和 nightly 发布渠道安装 Rust，且支持额外的交叉编译目标平台。
>
> 更多信息请查看 [`rustup` documentation](https://github.com/rust-lang-nursery/rustup.rs/blob/master/README.md)。

> ### 配置 `PATH` 环境变量
>
> 在 Rust 开发环境中，所有工具都安装到 `~/.cargo/bin` 目录， 并且您能够在这里找到 Rust 工具链，包括 `rustc`、`cargo` 及 `rustup`。
>
> 因此，Rust 开发者们通常会将此目录放入 [`PATH` 环境变量](https://en.wikipedia.org/wiki/PATH_(variable))。在安装时，`rustup` 会尝试配置 `PATH`， 但是因为不同平台、命令行之间的差异，以及 `rustup` 的 bug，对于 `PATH` 的修改将会在重启终端、用户登出之后生效，或者有可能完全不会生效。
>
> 当安装完成之后，如果在控制台运行 `rustc --version` 失败，这是最可能的原因。


## rustup

Rust编译器分为三个频道：修复了大多数Bug，但也不能用实验功能的Stable；等待观察成为Stable的Beta；以及有着最多Bug和Feature的Nightly。

Rust玩家需要在三个版本之间切换是十分痛苦的事情，有人做了切换工具multirust，之后被官方招安，改名为[rustup并成为默认的安装途径](https://github.com/rust-lang-nursery/rustup.rs)。如果需要帮助可以参考[这篇文章](https://github.com/rustcc/RustPrimer/blob/master/install/rustup.md)。

安装完成后视情况请定期运行 `rustup update`。不使用 Nightly 的话一般不到两个月更新一次。

## 源

这是一片神奇的土地，很多时候全球都能下载下来的在这片土地上就下载不下来。

感谢[中科大镜像有 Rust 源](https://lug.ustc.edu.cn/wiki/mirrors/help/rust-static) 这个源帮助下载 Rust 编译器等静态文件。

[crates.io](https://crates.io/) 是 Rust 包的网站，类似于NPM。so you know that, 这是[另一个镜像](https://lug.ustc.edu.cn/wiki/mirrors/help/rust-crates?s%5B%5D=rustt)。

以前有报告称，因为代码补全插件的bug，使用这个镜像会导致代码补全不可用，如果出现这种情况请切换回原本的源并且大喊：**fuck GFW**。然后用文本编辑器打开 `~/.cargo/config`

~~~ini
[http]
proxy = "[socks5://]server:<port>"
~~~

refer [1](https://github.com/rust-lang/cargo/issues/636) [2](https://github.com/rust-lang/cargo/issues/3596)

## RLS

**如果不使用 Visual Studio Code 本节可以跳过。**

RLS是Rust Language Server的简写，微软提出编程语言服务器的概念，将IDE的一些编程语言相关的部分由单独的服务器来实现，比如说代码补全、跳转定义、查看文档等等。这样只用给不同编辑器或者IDE实现客户端接口就好了。

Rust就是这个概念最积极的先行者，RLS是官方的，可预见的未来也是编辑器最主要的帮手。

RLS的安装请查阅[项目README](https://github.com/rust-lang-nursery/rls#setup)，也是rustup轻松完成。但因为目前部分功能还依赖Racer来实现，需要配置Racer的环境变量（不必安装），所以请参阅下文关于 `RUST_SRC_PATH` 环境变量的部分。

## Racer 代码补全

**如果使用 Intellij Rust 本节可以跳过。**

Racer是Rust代码补全库，被很多编辑器插件所需要，安装：

~~~shell
cargo install racer
~~~

代码补全需要源代码。以前需要下载源代码，手动放到某处并且定期更新，现在有了rustup很方便：

~~~shell
rustup component add rust-src
~~~

之后需要配置环境变量，新版的Racer[似乎能自动探测](https://github.com/phildawes/racer/pull/598)了，不过这里以防万一还是写一下。因为rustup使得rust编译器的版本可以随时切换，所以环境变量不能写死，从这个[issue](https://github.com/phildawes/racer/issues/595)可以看到很聪明的做法，设置环境变量为：

~~~shell
export RUST_SRC_PATH="$(rustc --print sysroot)/lib/rustlib/src/rust/src"
~~~

就能根据当前的Rust频道自动设置源代码地址了。

（但实际上强行设定为Nightly其实也不会有什么为问题…）

## rustfmt 和 rust-clippy

都是很重要的工具，配置起来也没什么麻烦的，就放在一起简单介绍一下。

这些都可以作为cargo的子模块，如果要学rust不可能不知道cargo。作为Rust最常用的有力工具，广受好评的cargo提供对项目的依赖管理、Build、文档生成、发布等等，还可以被插件扩展，下面这几个就是必装的cargo插件。

### [clippy](https://github.com/Manishearth/rust-clippy)

有点linter的感觉，分析你的源代码，检查哪些地方写得不地道可以改善。

可以作为项目依赖安装在编译时弹警告，但更好的做法是作为cargo的插件，手动或者被编辑器插件调用：

~~~shell
cargo install clippy
~~~

### [rustfmt](https://github.com/rust-lang-nursery/rustfmt)

顾名思义，格式化整个项目。commit 之前跑一遍吧。


<i>最后附赠一个编译器插件 [Herbie lint for Rust](https://github.com/mcarton/rust-herbie-lint) 检测不稳定的浮点数运算，Haskell 也有。</i>

## 编辑器

这里有[一份编辑器对Rust支持的表](https://areweideyet.com/)，没有更新最新的进展，但是可以大致看一下，根据自己喜欢的编辑器来挑选。

这里我主要推荐 [Visual Studio Code](https://code.visualstudio.com/) 主要是方便简单开箱即用，而且是目前RLS主要支持的编辑器。

（其次推荐[Intellij Rust](https://github.com/intellij-rust/intellij-rust)，作为Intellij插件，他们用自己写的逻辑而不是Racer补全，如果遇到问题了可以试试这个。）

语言插件请用[Rust](https://github.com/editor-rs/vscode-rust)，而不是停止维护的[Rusty Code](https://github.com/saviorisdead/RustyCode)。

![vscode-rust](/media/vscode-rust.png)

不过其实现在不管是 RLS 还是插件都是不是特别完善的状况，会遇到一些问题，但总体上还是绝对可用的。
