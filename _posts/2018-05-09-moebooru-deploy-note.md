---
layout: post
title: Moebooru部署笔记
category: dev
summary: 本文介绍流行的 weeaboo 贴图版 moebooru 在 Ubuntu 16.04 下的部署
typora-root-url: ../
typora-copy-images-to: ../media
---

[Moebooru](https://github.com/moebooru/moebooru)是流行的贴图版程序，可以放很多好东西。

主要参考的[这篇文章](https://twkrsplace.ru/posts/ruby-rose-moebooru-deployment/)，但是有不少区别。

机器是Ubuntu 16.04。安装在 CentOS 的尝试失败了，因为没搞懂PostgreSQL的各种依赖。

可能因为时效而失效，发现到的人可以邮件提醒我。

## 安装需要的依赖

```bash
apt update && apt upgrade
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install nodejs imagemagick jhead libxslt-dev libyaml-dev git libreadline-dev libpcre3-dev libssl-dev build-essential postgresql-server-dev-all postgresql postgresql-contrib nginx
```

[Node.Js 安装参考的此处](https://nodejs.org/en/download/package-manager/)，node 是被需要的。

`apt-get` 这些依赖都是moebooru的README里面写的，但是各个发行版的包名不同。

## 创建用户

```bash
adduser moebooru --disabled-password
```

创建一个独立的用户，剩余的东西几乎都在这个用户上做。

用户禁用了密码，只能用`su`等方式登陆。

## 配置数据库

```bash
sudo -u postgres psql
```

用管理员进入数据库的命令行。

```bash
CREATE user moebooru WITH password 'your_password' CREATEDB;
ALTER ROLE moebooru superuser;
\q
```

创建一个和刚才的 Linux 用户同名的数据库用户，然后将它改为超级用户。普通用户在后面的步骤会遇到权限问题，所以只是权宜之计，之后要改回来应该也行。

## 用户内

```bash
sudo -i -u moebooru
```

登入用户。然后安装 rbenv：

```bash
git clone https://github.com/rbenv/rbenv.git ~/.rbenv
cd ~/.rbenv && src/configure && make -C src
echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(rbenv init -)"' >> ~/.bashrc
# Restart shell
exec bash
# Check if rbenv is correctly installed
type rbenv
# Install ruby-build as rbenv plugin
git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build
cd ~
rbenv install 2.5.1
rbenv global 2.5.1
```

这里参考的是[mastodon的文档](https://github.com/tootsuite/documentation/blob/d9ea83d90826d09ea1061369782489f6fd36c1a3/Running-Mastodon/Production-guide.md#nodejs-and-ruby-dependencies)。

## 安装配置 moebooru

```bash
git clone https://github.com/moebooru/moebooru.git ~/live

cd live

mkdir public/data
mkdir -p public/data/{avatars,frame,frame-preview,image,inline,jpeg,preview,sample,search}

cp config/database.yml.example config/database.yml
cp config/local_config.rb.example config/local_config.rb
bundle exec rake secret
```

下载代码、初始化目录、复制配置文件、最后一步生成密钥。

然后复制生成出来的密钥，去修改 `config/local_config.rb` 然后修改 `config/database.yml`。

之后就可以初始化了：

```bash
bundle exec rake db:create
bundle exec rake db:reset
bundle exec rake db:migrate
bundle exec rake i18n:js:export
bundle exec rake assets:precompile
```

## 外围设施配置

从moebooru账户登出。

然后编辑 `/etc/nginx/nginx.conf` 。这些属性值是建议的：

```nginx
client_max_body_size 200m;
sendfile        on;
keepalive_timeout  65;
gzip  on;
```

在`/etc/nginx/sites-avaliable/` 里面增加一个 Nginx 虚拟主机文件`moebooru`：

```nginx
server {
    root /home/moebooru/live/public;
    listen  80;
    server_name _;
    location / { try_files /cache/$uri /cache/$uri.html $uri @moe; }
    location @moe {
        expires off;
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_redirect off;
        proxy_set_header Host $host:$server_port;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

然后再在`/etc/nginx/sites-enable/`里面增加软链接：

```bash
ln -s ../sites-avaliable/moebooru
```

最后用supervisor来管理服务器进程，在 `/etc/supervisor/conf.d/moebooru.conf`：

```ini
[program:moebooru]
command=/home/moebooru/.rbenv/shims/bundle exec unicorn
user=moebooru
directory=/home/moebooru/live/
```

启动moebooru

```bash
sudo supervisorctl start moebooru
```

以上。
