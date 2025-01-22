---
title: Redis实现投票机制的思路
date: 2025-01-22 11:25:00
categories:
- bluebell
---

`zset`每一个元素都有一个与之对应的分数，分数用于排序

设计两个`zset`（有序集合）key分别对应`post:time:`和`post:score:`，即帖子对应时间和分数，对应按照时间查找和按照分数查询

哪个用户对哪个帖子投票投的是赞成还是反对也要记录，再设计一个key为`post:voted` 



`:`分割key，相当于命名空间，方便查询和拆分

声明常量，可以写一个前缀`KeyPrefix`表明命名空间，方便业务拆分，每个键可以点名数据类型`KeyPostTimeZset`



首先对redis的数据结构没有非常深入的认识和了解，也没有真实地设计经验，所以看起来很迷茫。

`post:time`是一个zset，postId->time

`post:score:`是一个zset，posiId->score

`post:voted:<userId>`对应多个zset，每个zset记录一个用户的投票情况 