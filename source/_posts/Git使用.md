---
title: Git使用
index_img: "https://git-scm.com/images/logos/2color-lightbg@2x.png"
date: 2025-01-22 11:22:00
categories:
- Git
---
# 说明

此笔记是根据`progit`提炼出来的Git基本使用操作，后续可能还会根据日常使用增删内容。

# Git配置

## 双配置

双配置意思是对Gitee和Github分别生成SSH密钥对，两个密钥对相互独立，互不干扰，但是其实用同一个密钥对问题也不大。

1. 生成新的用于 Gitee 的 SSH 密钥对：

   ```
   ssh-keygen -t rsa -f C:\Users\许伟强\.ssh\id_rsa_gitee -C "2629162585@qq.com"
   ```

2. 生成新的用于 GitHub 的 SSH 密钥对：

   ```
   ssh-keygen -t rsa -f C:\Users\许伟强\.ssh\id_rsa_github -C "2629162585@qq.com"
   ```

3. 配置 SSH 配置文件：

   在 `~/.ssh` 目录下创建一个名为 `config` 的文件（如果不存在），并在其中添加以下内容：

   ```
   # Gitee
   Host gitee.com
   HostName gitee.com
   User git
   IdentityFile ~/.ssh/id_rsa_gitee
   
   # GitHub
   Host github.com
   HostName github.com
   User git
   IdentityFile ~/.ssh/id_rsa_github
   ```

4. 将生成的 Gitee 的公钥添加到 Gitee 中：

   打开 Gitee 网站，进入个人设置，找到 SSH 公钥相关设置，将 `~/.ssh/id_rsa_gitee.pub` 文件中的内容粘贴进去。

5. 将生成的 GitHub 的公钥添加到 GitHub 中：

   打开 GitHub 网站，进入设置页面，找到 SSH and GPG keys 选项，将 `~/.ssh/id_rsa_github.pub` 文件中的内容粘贴进去。

6. 测试连接：

   分别执行以下命令测试与 Gitee 和 GitHub 的连接：

   ```
   ssh -T git@gitee.com
   ssh -T git@github.com
   ```



# Git概念

Git是个分布式版本控制工具，支持多人协同，可以保存和管理不同版本的记录。

Git 更像是把数据看作是对小型文件系统的一系列快照

## 三种状态

 三种状态——已提交（committed）、已修改（modified） 和 已暂存（staged），对应工作区、暂存区以及Git目录

- 已修改表示修改了文件，但还没保存到数据库中。 

- 已暂存表示对一个已修改文件的当前版本做了标记，使之包含在下次提交的快照中。

- 已提交表示数据已经安全地保存在本地数据库中。

# Git使用（基础）

## 获取Git仓库

1. 将尚未进行版本控制的本地目录**转换**为Git仓库 

   - 切换到项目目录后，执行以下命令来创建一个名为`.git`的子目录，包含初始化Git仓库的必须文件。

     ```
     git init
     ```

   - 然后就可以开始追踪文件并初始提交，通过git add命令来追踪文件变化并提交到暂存区，例如以下命令添加了.c后缀的源文件和LICENSE到暂存区，或者叫做开始文件**追踪**，之后提交到了仓库中。

     ```
     git add *.c
     git add LICENSE
     git commit -m 'initial project version'
     ```

2. 从服务器上**克隆**一个已经存在的Git仓库

   - 使用`git clone <url> <name>`将云端仓库克隆到当前目录之下，name是可选参数，对应克隆到本地的仓库的目录名字，也可以不写，那么本地仓库的名字和云端相同。

     ```
     git clone <url> <name>
     ```

## 记录更新

你工作目录下的每一个文件都不外乎这两种状态：**已跟踪** 或 **未跟踪**。 

Untracked-》Unmodified-》Modified-》Staged（暂存）![文件状态周期](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/%E6%96%87%E4%BB%B6%E7%8A%B6%E6%80%81%E5%91%A8%E6%9C%9F.png)

### 状态查看

```
git status
```

使用`git status`命令查看哪些文件处于什么状态，git会详细说明情况。 git status -s 命令可查看简略版信息。??为未追踪，A(Add)表示提交到暂存区，M(Modified)表示已修改，输出有两栏（左为暂存区，右为工作区）。左侧M表示修改的文件已经提交到暂存区中，两个M表示该文件先前已经被修改且提交到了暂存区，但是现在有新的修改还没有提交。

```
$ git status -s
 M README
MM Rakefile
A lib/git.rb
M lib/simplegit.rb
?? LICENSE.txt
```

### 跟踪文件

将文件从未追踪转变为追踪，

```
git add <file>
```

### 忽略文件

编写.gitignore来忽略对某些文件的Git管理，这样他们就不会出现在未追踪文件列表中了。

#### glob 模式

glob 模式是指 shell 所使用的**简化了的正则表达式**。 星号（*）匹配零个或多个任意字符；[abc] 匹配任何一个列在方括号中的字符 （这个例子要么匹配一个 a，要么匹配一个 b，要么匹配一个 c）； 问号（?）只匹配一个任意字符；如果在方括号中使用短划线分隔两个字符， 表示所有在这两个字符范围内的都可以匹配比如 [0-9] 表示匹配所有 0 到 9 的数字）。 使用**两个星号`**`表示匹配任意中间目录**，比如 a/**/z 可以匹配 a/z 、 a/b/z 或 a/b/c/z 等。

#### 编写规范

-  所有空行或者以 # 开头的行都会被 Git 忽略。
-  可以使用标准的 glob 模式匹配，它会**递归**地应用在整个工作区中。
-  匹配模式可以以（/）开头**防止递归**。
-  匹配模式可以以（/）结尾**指定目录**。
-  要忽略指定模式以外的文件或目录，可以在模式前加上**叹号（!）取反**。

### 查看具体修改

查看尚未暂存的文件（也就是工作目录的modified文件）修改更新。

```
git diff
```

查看暂存区的修改更新，注意是和上次commit比较。

```
git diff --staged
# or #
git diff --cached
```

### 提交更新

每次准备提交前，先用 git status 看下，你所需要的文件是不是都已暂存起来了， 然后再运行提交命令

```
git commit
```

然后就会让你输入信息备注这次commit。

更详细的内容修改提示可以用 -v 选项查看，这会将你所作的更改的 diff 输出呈现在编辑器中，以便让你知道本次提交具体作出哪些修改。

在 commit 命令后添加 -m 选项，将提交信息与命令放在同一行。

```
git commit -m <message>
```

在 commit 命令后添加 - a 选项，Git 就会自动把所有已经跟踪过的文件暂存起来一并提交，从而跳过 git add 步骤

### 移除文件

移除文件是从工作目录和暂存区中删除指定的文件，并记录这次删除操作。git rm不能删除在工作区中有修改但没有暂存的文件，这种情况要`-f`才能强制删除。也就是说不加参数的git rm只能删除工作区和暂存区保持一致的文件。

```
git rm <file>
```

如果仅仅是想从暂存区移除，在本地不删除文件的话

```
git rm --cashed <file>
```

同时git有一些特殊的文件扩展匹配方式，例如

命令后面可以列出文件或者目录的名字，也可以使用 glob 模式。**注意到星号 * 之前的反斜杠  **。此命令删除 log/ 目录下扩展名为 .log 的所有文件。 

```
$ git rm log/\*.log
```

该命令会删除所有名字以 ~ 结尾的文件。

```
$ git rm \*~
```

### 移动文件

重命名文件，改名。Git自动推测出来的

```
 git mv file_from file_to
```

### 查看提交历史

不传入任何参数的默认情况下，git log 会按时间先后顺序列出所有的提交，最近的更新排在最上面。 

```
git log
```

其中一个比较有用的选项是 -p 或 --patch ，它会显示每次提交所引入的差异（按 **补丁** 的格式输出）。 你也可以限制显示的日志条目数量，例如使用 -2 选项来只显示最近的两次提交。比如你想看到每次提交的简略统计信息，可以使用 --stat 选项。

另一个非常有用的选项是 --pretty。 这个选项可以使用不同于默认格式的方式展示提交历史。  这个选项可以使用不同于默认格式的方式展示提交历史。 这个选项有一些内建的子选项供你使用。 比如 oneline 会将每个提交放在一行显示，在浏览大量的提交时非常有用。 另外还有 short，full 和 fuller 选项，它们展示信息的格式基本一致，但是详尽程度不一：最有意思的是 format ，可以定制记录的显示格式。 这样的输出对后期提取分析格外有用——因为你知道输出的格式不会随着 Git 的更新而发生改变：

。。。有点多

### 撤销操作

git status给了很多操作的提示

#### 修改提交

修改最近一次的提交使用`git commit --amend`命令，来更正一些遗忘的操作。

例如，你提交后发现忘记了暂存某些需要的修改，可以像下面这样操作：

```
$ git commit -m 'initial commit'
$ git add forgotten_file
$ git commit --amend
```

最终你只会有一个提交——第二次提交将代替第一次提交的结果。

#### 取消暂存

在 “Changes to be committed” 文字正下方，提示使用 `git reset HEAD <file>…` 来取消暂存。reset很危险。

#### 撤销修改

 `"git checkout -- <file>..."`用于忽略工作目录中的修改，Git会用最近提交的版本来覆盖文件，也很危险。 除非你确实清楚不想要对那个文件的本地修改了，否则请不要使用这个命令。

在 Git 中任何 **已提交** 的东西几乎总是可以恢复的。然而，任何你未提交的东西丢失后很可能再也找不到了。

 `"git checkout <commitId> -- <file_path_to_rep>..."`将（多个）文件回退到commitId对用的版本

撤销git commit --amend

```
git reset HEAD@{1} 
```

### 恢复文件

将工作区某个文件恢复到上次提交或暂存（如果有暂存就恢复到暂存，否则是恢复到提交的），但是如果有删除操作被放到暂存区的话会报错哦

```
git restore <file_name>
```

将工作区针对某个文件的操作撤销暂存，**注意**删除操作无法恢复已经被删除的文件

```
git restore --staged <file_name>
```

eg：现在有test.py和test.go两个文件，都分别被commit到本地仓库过了。

1. 现在执行`rm test.go test.py`，此操作只是在工作区删除了test.go和test.py，删除操作没有放入暂存区，此时我们可以执行`git restore test.go test.py`来恢复test.go和test.py到上一次提交的状态。

   ```bash
   # rm test.go test.py
   # git status
   On branch master
   Your branch is ahead of 'origin/master' by 2 commits.
     (use "git push" to publish your local commits)
   
   Changes not staged for commit: 
     (use "git add/rm <file>..." to update what will be committed)
     (use "git restore <file>..." to discard changes in working directory)
           deleted:    test.go
           deleted:    test.py
   
   no changes added to commit (use "git add" and/or "git commit -a")
   # git restore test.go test.py
   # ls
   README.md  test.go  test.py
   ```

2. 现在执行`git rm test.go test.py`，此操作先在工作区删除了test.go和test.py，然后将删除操作放入了暂存区，此时不能直接执行`git restore test.go test.py`来恢复test.go和test.py到上一次提交的状态，会报错：

   ```
   error: pathspec 'test.go' did not match any file(s) known to git
   error: pathspec 'test.py' did not match any file(s) known to git
   ```

   应该先将暂存区中的删除记录撤销，然后再尝试恢复文件到上一次提交。先执行`git restore --staged  test.go test.py`撤销删除记录，再执行`git restore test.go test.py`恢复到上次提交。

   ```bash
   # git rm test.go test.py
   rm 'test.go'
   rm 'test.py'
   # ls
   README.md
   # git status
   On branch master
   Your branch is ahead of 'origin/master' by 2 commits.
     (use "git push" to publish your local commits)
   
   Changes to be committed:
     (use "git restore --staged <file>..." to unstage)
           deleted:    test.go
           deleted:    test.py
   
   # git restore  test.go test.py
   error: pathspec 'test.go' did not match any file(s) known to git
   error: pathspec 'test.py' did not match any file(s) known to git
   # git restore --staged  test.go test.py
   # git status
   On branch master
   Your branch is ahead of 'origin/master' by 2 commits.
     (use "git push" to publish your local commits)
   
   Changes not staged for commit:
     (use "git add/rm <file>..." to update what will be committed)
     (use "git restore <file>..." to discard changes in working directory)
           deleted:    test.go
           deleted:    test.py
   
   no changes added to commit (use "git add" and/or "git commit -a")
   # git restore test.go test.py
   # git status
   On branch master
   Your branch is ahead of 'origin/master' by 2 commits.
     (use "git push" to publish your local commits)
   
   nothing to commit, working tree clean
   # ls
   README.md  test.go  test.py
   ```


## 合并提交

`git rebase -i HEAD~3`或者`git rebase -i 51efaef517abdbf674478de6073c12239d78a56a` （第一个commit的id）将会将三个提交压缩为一个提交。

提交后会跳出交互界面供修改：

```
pick 1234567 第一次提交的描述信息
pick 2345678 第二次提交的描述信息
pick 3456789 第三次提交的描述信息

# Rebase 4567890..3456789 onto 4567890 (3 commands)
#
# Commands:
# p, pick <commit> = use commit
# r, reword <commit> = use commit, but edit the commit message
# e, edit <commit> = use commit, but stop for amending
# s, squash <commit> = use commit, but meld into previous commit
# f, fixup <commit> = like "squash", but discard this commit's log message
# x, exec <command> = run command (the rest of the line) using shell
# b, break = stop here (continue rebase later with 'git rebase --continue')
# d, drop <commit> = remove commit
# l, label <label> = label current HEAD with a name
# t, reset <label> = reset HEAD to a label
# m, merge [-C <commit> | -c <commit>] <label> [# <oneline>]
# .       create a merge commit using the original merge commit's
# .       message (or the oneline, if no original merge commit was
# .       specified). Use -c <commit> to reword the commit message.
#
# These lines can be re-ordered; they are executed from top to bottom.
#
# If you remove a line here THAT COMMIT WILL BE LOST.
#
# However, if you remove everything, the rebase will be aborted.
#
# Note that empty commits are commented out
```

### 交互界面命令说明

```plaintext
# Commands:
# p, pick <commit> = use commit
# r, reword <commit> = use commit, but edit the commit message
# e, edit <commit> = use commit, but stop for amending
# s, squash <commit> = use commit, but meld into previous commit
# f, fixup <commit> = like "squash", but discard this commit's log message
# x, exec <command> = run command (the rest of the line) using shell
# b, break = stop here (continue rebase later with 'git rebase --continue')
# d, drop <commit> = remove commit
# l, label <label> = label current HEAD with a name
# t, reset <label> = reset HEAD to a label
# m, merge [-C <commit> | -c <commit>] <label> [# <oneline>]
# .       create a merge commit using the original merge commit's
# .       message (or the oneline, if no original merge commit was
# .       specified). Use -c <commit> to reword the commit message.
```

这部分是对可用命令的说明，常用命令解释如下：

- **`pick (p)`**：使用该提交，不做任何修改。
- **`reword (r)`**：使用该提交，但允许你编辑提交信息。
- **`edit (e)`**：使用该提交，但在处理到该提交时暂停，允许你对该提交进行修改（如添加或删除文件）。
- **`squash (s)`**：将该提交合并到前一个提交中，合并后会让你编辑合并后的提交信息。
- **`fixup (f)`**：类似于 `squash`，但会丢弃该提交的日志信息，直接使用前一个提交的信息。
- **`drop (d)`**：删除该提交记录。

现在用的到的是将第一条提交打p，后面的提交都打s，这样会让我编辑决定合并后的提交信息。

采用当前操作的日期

```
git rebase -i <base-commit> --committer-date-is-author-date
```

# 日常使用

## 代码同步

在某个本地分支上，丢弃本地状态，强制同步本地到仓库版本

```
git fetch --all && git reset --hard origin/<分支> 
```

```
git fetch --origin && git reset --hard origin/adapter-5.3.0
```

切换到远程仓库分支，head 会 detach

```
git fetch --origin && git checkout origin/<分支>
```

## 创建分支

```
git checkout -b <new-branch-name>
```

## 切换分支前丢弃冲突

强制删除未跟踪的目录和文件，然后切换分支

```
git clean -fd
git checkout origin/5.3.0
```

## 推送远程没有的分支

当前分支 adapter-5.3.0 没有对应的上游分支，为推送当前分支并建立与远程上游的跟踪，使用

```
git push --set-upstream origin adapter-5.3.0
```

## **对比两个提交并列出不同的文件**

只列出名字

```
git diff --name-only <commit-hash-1> <commit-hash-2>
```

| 需求                           | 命令                                           |
| ------------------------------ | ---------------------------------------------- |
| 列出不同文件                   | `git diff --name-only <commit-1> <commit-2>`   |
| 查看详细差异                   | `git diff <commit-1> <commit-2>`               |
| 统计改动数量                   | `git diff --stat <commit-1> <commit-2>`        |
| 显示改动类型（新增/修改/删除） | `git diff --name-status <commit-1> <commit-2>` |

## 终止合并

```
git merge --abort
```

## IDEA图形化界面合并提交

https://blog.csdn.net/yuec1998/article/details/118460431

## 修改分支名称

在本地分支

```
# 切换到目标分支
git checkout feature-old

# 重命名分支
git branch -m feature-new
```

对远程

```
# 删除远程旧分支
git push origin --delete feature-old

# 推送新分支到远程
git push origin feature-new

# 设置新分支为默认上游分支
git branch --set-upstream-to=origin/feature-new
```

## git-alias

使用别名提高效率，但是没有尝试，目前已经在终端配置了别名

Git Pro：https://git-scm.com/book/zh/v2/Git-%E5%9F%BA%E7%A1%80-Git-%E5%88%AB%E5%90%8D

https://zhuanlan.zhihu.com/p/52806571

## LF转换（无用）

在Win上我的Git自己会转换换行符。目前IDEA同步代码会出现较多的问题，LF、文件修改

- LF：

  **转换单个文件**

  使用 `dos2unix` 命令直接转换指定的文件：

  ```
  dos2unix guesttools/src/main/java/org/zstack/guesttools/APIGetGuestVmScriptExecutedRecordAndDetailMsg.java
  ```

  **批量转换多个文件**

  如果你需要转换整个目录下的所有文件，可以结合 `find` 命令一起使用：

  ```
  find . -type f -print0 | xargs -0 dos2unix
  ```

  这会递归地查找当前目录及其子目录下所有文件，并将它们从 DOS/Windows 格式转换为 Unix 格式。

- 文件修改：

  可能需要手动比较不同文件的修改，手动restore回退

## 修改时间

```
# 修改上次提交日期为当前时间
git commit --amend --no-edit --date "now"
```

## 切换远程仓库

```
git remote set-url origin http://dev.zstack.io:9080/jin.shen/zstack-utility.git
git fetch origin
```

## 项目内邮箱和用户名设置

```
PS D:\zstack\cloud\zstack-utility> git config user.name "weiqiang.xu"
PS D:\zstack\cloud\zstack-utility> git config user.email "weiqiang.xu@zstack.io"
```

```
PS D:\zstack\cloud\zstack-utility> git config --local --list
core.repositoryformatversion=0
core.filemode=false
core.bare=false
core.logallrefupdates=true
core.symlinks=false
core.ignorecase=true
remote.origin.url=http://dev.zstack.io:9080/jin.shen/zstack-utility.git
remote.origin.fetch=+refs/heads/*:refs/remotes/origin/*
branch.master.remote=origin
branch.master.merge=refs/heads/master
remote.upstream.url=http://dev.zstack.io:9080/zstackio/zstack-utility.git
remote.upstream.fetch=+refs/heads/*:refs/remotes/upstream/*
branch.metadata-5.3.0-ZSTACK-74105@@2.remote=origin
branch.metadata-5.3.0-ZSTACK-74105@@2.merge=refs/heads/metadata-5.3.0-ZSTACK-74105@@2
branch.adapter-ZSTAC-73178@@3.remote=origin
branch.adapter-ZSTAC-73178@@3.merge=refs/heads/adapter-ZSTAC-73178@@3
branch.ZSTAC-71896.remote=origin
branch.ZSTAC-71896.merge=refs/heads/ZSTAC-71896
user.name=weiqiang.xu
user.email=weiqiang.xu@zstack.io
```

## 修改上次提交的作者信息

```
git commit --amend --reset-author --no-edit
```

