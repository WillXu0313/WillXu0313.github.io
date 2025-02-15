---
title: Docker安装和Dockerfile入门
excerpt: 本片主要是Docker的简要介绍和在Ubuntu上配置镜像源安装Docker的过程，除此之外还简单讲解了Dockerfile的入门知识
index_img: "https://www.docker.com/wp-content/uploads/2023/08/logo-guide-logos-1.svg" 
date: 2025-01-22 10:59:00
categories:
- Docker
---
# Docker简介

Docker 可以让开发者打包他们的应用以及依赖包到一个轻量级、可移植的容器中，然后发布到任何流行的 Linux 机器上，也可以实现虚拟化。容器是完全使用沙箱机制，相互之间不会有任何接口（类似 iPhone 的 app）,更重要的是容器性能开销极低。

## 三个基本要素

1. 镜像（Image）

   Docker的镜像概念**类似于虚拟机里的镜像**(比如.ISO文件)，是一个只读的模板，一个独立的文件系统，**包括运行容器所需的数据**，可以用来创建新的容器，Dockerfile用来创建镜像。这里的镜像就如虚拟机创建时候使用的镜像类似。这个镜像便于移动,并且这个镜像我们可以交给任何人使用,其他人使用的时候也很方便,只需要将其实例化即可。
   例如：一个镜像可以包含一个完整的 ubuntu 操作系统环境，里面仅安装了MySQL或用户需要的其它应用程序。

2. 容器（Container）

   我觉得容器这个概念是最重要的

   Docker容器是由**Docker镜像创建的运行实例**，类似VM虚拟机，支持启动，停止，删除等。
   每个容器间是相互隔离的，容器中会运行特定的应用，包含特定应用的代码及所需的依赖文件。
   容器就类似与虚拟机中创建的**虚拟机系统**（Ubuntu）,之后我们所有的操作都是在容器中进行的,我们的程序也是运行在容器中。

3. 仓库（Repository）

   镜像便于传播,而仓库就是**专门用来传播镜像的地方**,有点类似与Github,或者你可以把他看成一个存放各种镜像的镜像商店

参考资料：[从零开始的Docker Desktop使用,Docker快速上手 （￣︶￣） Docker介绍和基础使用-CSDN博客](https://blog.csdn.net/qq_39611230/article/details/108641842)

# Docker安装

在Windows上，直接挂梯子去官网下载`Docker Desktop`，后续直接挂梯子用就好了。

在Linux上，官方源因为墙的问题连不上，而且我没有给服务器配代理，所以用的是国内阿里云的镜像源。**Ubuntu22.04**下使用阿里云Docker镜像源的Docker安装说明如下：

## 1. 添加阿里云Docker镜像源

首先，删除之前添加的Docker GPG密钥和APT源文件（如果有）：

```bash
sudo rm /usr/share/keyrings/docker-archive-keyring.gpg
sudo rm /etc/apt/sources.list.d/docker.list
```

然后，添加阿里云Docker镜像源的GPG密钥：

```bash
curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

接着，添加阿里云的APT源：

```bash
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

## 2. 更新APT包索引

使用新添加的APT源更新包索引：

```bash
sudo apt update
```

## 3. 安装Docker

使用以下命令安装Docker：

```bash
sudo apt install docker-ce
```

## 4. 启动Docker并设置开机自启动

启动Docker服务并设置为开机自启动：

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

## 5. 验证安装

通过运行一个测试镜像来验证Docker是否安装成功：

```bash
sudo docker run hello-world
```

## 6. 配置国内镜像源

原文链接：https://blog.csdn.net/qq_21583139/article/details/105349170

1. 在docker下面路径中创建并添加或修改镜像源

   ```
   sudo vim /etc/docker/daemon.json
   ```

2. 在文档里添加如下内容，可以多加几个镜像源，国内不太稳定。（至于如何添加——insert，然后退出保存：w，：q）

   ```json
   {
       "registry-mirrors": [
       	"https://docker.registry.cyou"
       ]
   }
   ```

3. 退出保存后，记得一定要重启服务

   ```
   systemctl restart docker
   sudo systemctl status docker
   ```

4. 再次验证

   ```
   sudo docker run hello-world
   ```

5. 最终效果是收到Hello from Docker！

## 7. 可选：将当前用户添加到`docker`组

为了避免每次运行`docker`命令都使用`sudo`，可以将当前用户添加到`docker`组：

```bash
sudo usermod -aG docker $USER
```

然后，退出当前终端并重新登录以应用组更改。

# Dockerfile

## 基础镜像

FROM指令：基于FROM指定的基础镜像开始构建镜像

RUN指令：用于执行后续的命令行指令，有shell和exec两种格式，exec格式相当于把每段命令用冒号隔开了，差别不大。

```bash
RUN <命令行命令>
# <命令行命令> 等同于，在终端操作的 shell 命令。

RUN ["可执行文件", "参数1", "参数2"]
# 例如：
# RUN ["./test.php", "dev", "offline"] 等价于 RUN ./test.php dev offline
```

Dockerfile的指令每执行一次都会在 docker 上新建一层，可以使用`&&`符号连接命令，这样只会创建一层镜像。

例如：

```bash
FROM centos
RUN yum -y install wget
RUN wget -O redis.tar.gz "http://download.redis.io/releases/redis-5.0.3.tar.gz"
RUN tar -xvf redis.tar.gz
```

以上执行会创建 3 层镜像。可简化为以下格式，只会创建一层：

```bash
FROM centos
RUN yum -y install wget \
    && wget -O redis.tar.gz "http://download.redis.io/releases/redis-5.0.3.tar.gz" \
    && tar -xvf redis.tar.gz
```

## 开始构建

在当前目录下构建镜像的命令如下：

```
$ docker build -t <imageName> .
```

**.** 是上下文路径，docker在构建镜像时会把路径下的所有内容打包，是可指定的。

docker 的运行模式是 C/S，我们本机是 C，docker 引擎是 S。实际的构建过程是在 docker 引擎下完成的，无法用到本机的文件。

上下文路径下不要放无用的文件。

## 更多命令

| 指令        | 说明                                                         | 陌生程度 |
| ----------- | ------------------------------------------------------------ | -------- |
| FROM        | 指定基础镜像                                                 |          |
| LABEL       | 添加镜像的元数据，K/V形式                                    | *        |
| RUN         | 在**构建**过程中在镜像中执行命令                             |          |
| CMD         | 指定**容器创建**时的默认命令（可覆盖）                       |          |
| ENTRYPOINT  | 指定容器创建时的主要命令（不可覆盖）                         |          |
| EXPOSE      | 声明容器运行时监听的特定网络端口                             |          |
| ENV         | 在容器内部设置环境变量                                       |          |
| ADD         | 将文件、目录或远程URL复制到镜像中                            | *        |
| COPY        | 将文件或目录复制到镜像中                                     |          |
| VOLUME      | 为容器创建挂载点或声明卷                                     | *        |
| WORDIR      | 指定后续指令的工作目录                                       | *        |
| USER        | 指定后续指令的用户上下文。                                   | *        |
| ARG         | 定义在构建过程中传递给构建器的变量，可使用 "docker build" 命令设置。 | **       |
| ONBUILD     | 当该镜像被用作另一个构建过程的基础时，添加触发器。           | **       |
| STOPSIGNAL  | 设置发送给容器以退出的系统调用信号。                         | **       |
| HEALTHCHECK | 定义周期性检查容器健康状态的命令。                           | *        |
| SHELL       | 覆盖Docker中默认的shell，用于RUN、CMD和ENTRYPOINT指令。      | **       |
|             |                                                              |          |

### COPY

```
COPY <源路径> <目标路径 >
```

ADD推荐用COPY

### CMD

**注意**：只有最后一个CMD指令会被执行。

**作用**：为启动的容器指定默认要运行的程序，程序运行结束，容器也就结束。CMD 指令指定的程序可被 docker run 命令行参数中指定要运行的程序所**覆盖**。

**格式**：

```
CMD <shell 命令> 
```

推荐使用以下格式

```
CMD ["<可执行文件或命令>","<param1>","<param2>",...] 
```

```
CMD ["<param1>","<param2>",...]  # 该写法是为 ENTRYPOINT 指令指定的程序提供默认参数
```

### ENTRYPOINT

不会被docker run命令行参数覆盖，

但是, 如果运行 docker run 时使用了 --entrypoint 选项，将覆盖 ENTRYPOINT 指令指定的程序，因此在执行 docker run 的时候可以指定 ENTRYPOINT 运行所需的参数

如果 Dockerfile 中如果存在多个 ENTRYPOINT 指令，仅最后一个生效。

当同时使用 ENTRYPOINT 和 CMD 时，CMD 的内容会作为参数传递给 ENTRYPOINT 指定的命令。在docker run时候可以指定参数传递给 ENTRYPOINT 指定的命令，若docker run没有传递参数则执行CMD传递参数给ENTRYPOINT 指定的命令；若docker run传递参数则执行新的参数传递给ENTRYPOINT 指定的命令。例如：

假设已通过 Dockerfile 构建了 nginx:test 镜像：

```
FROM nginx

ENTRYPOINT ["nginx", "-c"] # 定参
CMD ["/etc/nginx/nginx.conf"] # 变参 
```

1、不传参运行

```
$ docker run  nginx:test
```

容器内会默认运行以下命令，启动主进程。

```
nginx -c /etc/nginx/nginx.conf
```

2、传参运行

```
$ docker run  nginx:test -c /etc/nginx/new.conf
```

容器内会默认运行以下命令，启动主进程(/etc/nginx/new.conf:假设容器内已有此文件)

```
nginx -c /etc/nginx/new.conf
```

### ENV

设置环境变量，定义了环境变量，那么在后续的指令中，就可以使用这个环境变量。

格式：

```
ENV <key> <value>
ENV <key1>=<value1> <key2>=<value2>...
```

### ARG

构建参数，与 ENV 作用一致。不过作用域不一样。ARG 设置的环境变量仅对 Dockerfile 内有效，也就是说只有 docker build 的过程中有效，构建好的镜像内不存在此环境变量。

构建命令 docker build 中可以用 --build-arg <参数名>=<值> 来覆盖。

格式：

```
ARG <参数名>[=<默认值>]
```
