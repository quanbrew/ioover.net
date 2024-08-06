---
layout: post
title: 在 PostgreSQL 中表示一棵树
date: 2018-11-19 18:58:58 +0800
category: dev
summary: TL;DR 利用 ltree 扩展
typora-root-url: ../
typora-copy-images-to: ../media
---

最近在尝试写一个笔记本，类似于*[org-mode](https://orgmode.org/)*以及*[workflowy](https://workflowy.com/)*的感觉，支持笔记的无穷层级嵌套。所以天然形成了一个树结构。

![dynalist](/media/dynalist.png)

对我来说这种结构的笔记本非常适合管理各种复杂的信息。

闲话少说。我在前端采用了imutable数据结构储存信息，但是在后端则需要找到一种储存树状数据的方式。[MongoDB](https://www.mongodb.com/)似乎有这些功能，但是我审美上难以接受这个项目。想了一下关于SQL和NoSQL的诸多梗，还是使用传统的SQL来表示数据了。

SQL数据库表示树状数据已经有很多资料了，[这篇知乎回答](https://www.zhihu.com/question/20417447/answer/15078011)帮了我很大的忙。

> Adjacency List：每一条记录存parent_id
>
> Path Enumerations：每一条记录存整个tree path经过的node枚举
>
> Nested Sets：每一条记录存 nleft和nright
>
> Closure Table：维护一个表，所有的tree path作为记录进行保存。

Adjacency List在查询所有后代的时候需要递归查询。本来最中意Closure Table，也就是另外维护一个查询后代关系的表，但是需要更多的空间。

通过 [stack overflow](https://stackoverflow.com/questions/2175882/how-to-represent-a-data-tree-in-sql)，我知道 PostgreSQL有一个用户贡献的扩展叫做[ltree](https://www.postgresql.org/docs/current/ltree.html)。从方法上，其实不外乎是Path Enumerations，i.e. 把经过的路径记录在一个字段上。但是因为是精心设计的用来表示树的字段，所以PostgreSQL可以高效地索引和搜索树状数据，并且有很多方便的操作。

~~~plsql
CREATE EXTENSION IF NOT EXISTS ltree; -- 启用扩展

CREATE TABLE nodes (
    id uuid PRIMARY KEY,
    path ltree NOT NULL UNIQUE,
);

CREATE INDEX node_path ON nodes USING GIST (path);
~~~

为了发挥潜能，对ltree类型的索引需要用GIST类型的。

ltree 类型是这样表示的 `label1.label2.label3` 其中`label`是限定为`[a-z][A-Z][0-9]_`的字符串，有些时候层级的名字可以用label表示（比如说名字空间），但也有些时候不能。

一个简单的方法是给每个节点一个UUID，然后ltree就表示为`6d0a48d0ac944a4caa74bd88dcc05ca8.d119af9537bb40158fcecd7d29147e6a`这种感觉。最好用base62把UUID编码以后储存，这样长度比较小。

可以在查询一棵树的时候抹去path，将树的表现方式封装出来。用一个JOIN就可以查询每个节点的parent，并且返回parent的id。

~~~plsql
SELECT
    L.id, R.id AS parent_id
FROM
	nodes L LEFT JOIN nodes R -- 自身 JOIN
    ON subpath(L.path, 0, -1) = R.path -- 查询父节点的路径
ORDER BY (R.id, L.path); -- 按照父节点排序，以便重建树
~~~

到目前为止我们就能用SQL很好地表达树状结构了，但是没办法很好地安排节点的位置。有一种繁琐的方法，可以把兄弟节点的顺序也编码进`path`。

节点之间的顺序是按树的*深度*优先遍历顺序进行的，对于兄弟节点按照字典序。

对于有索引的树来说，路径中的UUID其实是多余的，完全可以在路径中利用字典序安排节点的顺序。

`c < cc` 要在`cc`后面插入一个的话就只需要保证字典序在`cc`之后就行了，`ccc`或者`cd`都可以。在`c`之前插入的话就是`c < cb < cc`。在开头插入就是`b < c < cc`。

这种方法可以保证最小的更新次数。也能保证路径尺寸比较小。但是编码很复杂，当两个编码紧挨的时候还要考虑重排。

我现在还是用很普通的方法：维护一个单独的整形字段用来排序。