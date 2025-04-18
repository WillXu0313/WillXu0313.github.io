---
title: PowerShell-Alias
date: 2025-04-19 07:04:02
categories:
- OS
---

https://segmentfault.com/a/1190000015928399

# Alias定义

Linux修改常用alias，最好带参数

```
alias cdh='cd /home/xwq'
alias cdp='cd /home/xwq/zstack/premium'
alias cdpe='cd /home/xwq/zstack/premium/plugin-premium/externalapiadapter'
alias cdpt='cd /home/xwq/zstack/premium/test-premium'
alias cdu='cd /home/xwq/zstack-utility'
alias cdz='cd /home/xwq/zstack/'
alias cleaninstall='mvn clean install'
alias cp='cp -i'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias gia='git add .'
alias gib='git branch'
alias gic='git commit'
alias gica='git commit -a --amend'
alias gican='git commit -a --amend --no-edit'
alias gich='git checkout'
alias gich.='git checkout .'
alias gicm='git checkout master'
alias gid='git diff'
alias gifo='git fetch origin'
alias gifs='git fetch origin && git reset --hard'
alias gifu='git fetch upstream'
alias gil='git log'
alias gimo='git merge origin/master'
alias gimu='git merge upstream/master'
alias girt='git remote -v'
alias gis='git status'
alias grep='grep --color=auto'
alias l.='ls -d .* --color=auto'
alias ll='ls -l --color=auto'
alias loginmysql='mysql -u root -p'
alias ls='ls --color=auto'
alias lwc='ll |wc -l'
alias mv='mv -i'
alias mvnd='mvn -Dmaven.surefire.debug="-Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=5005 -Xdebug -Xnoagent -Djava.compiler=NONE"'
alias mvnt='mvn test -Djacoco.skip=true -Dtest= -T'
alias rm='rm -i'
alias rmmt='rm -rf management.log'
alias rq='rm -rf qemu-kvm-ev'
alias runM='mvn clean install -Dmaven.test.skip=true'
alias runP='./runMavenProfile premium'
alias sba='source ~/.bashrc'
alias startM='service mysql start'
alias which='alias | /usr/bin/which --tty-only --read-alias --show-dot --show-tilde'
```

Linux下，Alias是一个简单的文本替换，**支持附加参数**，后续跟的命令会生效。比如定义 `alias gid='git diff'` ，可以在gid后再加命令，例如一个比较commit不同：

```
gid fe22995a974e3c064f598b8134d153aa1ff0ceb8 49f2688387b4da1843ff66d9a6594c9a26be3eb6
```

但是如果有比较复杂的替换逻辑则需要使用函数。

# PowerShell定义

函数定义

```powershell
# Git 别名函数
function gia { git add . }
function gib { git branch }
function gic { git commit }
function gica { git commit -a --amend }
function gican { git commit -a --amend --no-edit }
function gich { git checkout $args }
function gich. { git checkout . }
function gicm { git checkout master }
function gid { git diff }
function gifo { git fetch origin }
function gifu { git fetch upstream }
function gifs { git fetch origin; git reset --hard }
function gil { git log }
function gimu { git merge upstream/master }
function gimo { git merge origin/master }
function girt { git remote -v }
function gis { git status }

function gifs {
    param (
        [Parameter(Mandatory=$true)]
        [string]$branch
    )
    git branch
    git fetch origin
    git reset --hard "$branch"
}
```

希望用函数替换：

```
git fetch origin && git reset --hard <仓库/分支>
```

```
function gifs {
    param (
        [Parameter(Mandatory=$true)]
        [string]$branch
    )
    git branch
    git fetch origin
    git reset --hard "$branch"
}
```

# 创建永久的别名（拷贝）

在PowerShell中直接使用`Set-Alias`或`New-Alias`命令创建的别名在关闭此Session后即会失效，防止此现象的方法是将此命令写入`Windows PowerShell profile`文件。
查看此文件在计算机中的位置：

```autoit
PS C:\> $profile
```

一般该文件在没有创建前是不存在的，使用以下命令为当前用户创建profile命令并返回文件地址：

```autoit
PS C:\> New-Item -Type file -Force $profile
```

一般创建的位置在`~\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1`
打开文件，键入文件内容为`Get-ChildItem -Name`创建别名`ls`：

```bash
function getFileName{
    Get-ChildItem -Name
}
Remove-Item alias:ls
Set-Alias ls getFileName
```

这里首先为`Get-ChildItem -Name`创建了方法`getFileName`作为中介，然后为该方法赋予别名`ls`，但是因为`ls`是Windows PowerShell中的默认别名，因此必须先删除再创建，所以先使用`Remove-Item`再使用`Set-Alias`或`New-Alias`。
以后每次在打开PowerShell会话框的时候其会先读取`$profile`文件中的内容。

试试效果：

```bash
PS D:\apktool> ls
apktool.bat
apktool.jar
```
