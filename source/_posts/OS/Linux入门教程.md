---
title: Linux入门教程
date: 2025-04-19 07:04:02
categories:
- OS
---

命令、简介：https://blog.csdn.net/bigbangbangbang1/article/details/131575669

目前先有概念，快速建立起整体框架和基本快捷使用。大致浏览了一遍，建立了概念和使用，更复杂的使用需要在实践中进行。

# 文件系统

## inode（索引节点）

https://blog.csdn.net/weixin_55767624/article/details/145737919

inode，即index node（索引节点），用于表示文件系统中的每个文件或目录。每一个文件或目录在创建时都会分配一个唯一的inode，包含了文件或目录的元数据信息。

inode包含的信息通常有：

- **文件类型**：比如普通文件、目录、符号链接等。
- **权限**：读、写、执行权限等。
- **所有者ID**和**组ID**：表明文件的所有者以及所属用户组。
- **文件大小**：以字节为单位的文件大小。
- **时间戳**：包括最后一次访问时间、内容修改时间、状态改变时间等。
- **指向数据块的指针**：实际存储文件内容的数据块的位置。

## 硬链接与软链接

软硬链接：https://mp.weixin.qq.com/s?__biz=MzIwNDQwMjIwNQ==&mid=2247483954&idx=1&sn=2fe835d6ca01817557e836bee6f157c5&chksm=96c1f940a1b6705655bc1cb58a2a0e4bdb0000f965a0b8b58a3ab5f27ebc1b6446a40d606011&scene=21#wechat_redirect

其中关于软链接要注意是绝对路径应该是错的：https://blog.csdn.net/Yonggie/article/details/131801160

硬链接——多个文件名指向同一个inode，删除任意一个文件不会影响到inode，前提是同一个文件系统

软链接——有点像Windows的快捷方式，存放的是文件路径，删除原先的文件就意味着软链接失效了，优点是可以跨文件系统使用