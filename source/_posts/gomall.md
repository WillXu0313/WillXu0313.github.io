---
title: gomall
date: 2025-01-22 22:17:07
tags: gomall
---

# CloudWeGo简介

CloudWeGo是字节跳动开源的微服务架构应用，主要有Go和Rust两种实现方式。该架构围绕Go、Rust语言开发，涵盖框架、编解码器、网络库与运行时、工具、中间件多个层面，各组件协同工作，为构建高性能分布式系统提供技术支撑。

1. **框架（Framework）**
    - **Kitex与Hertz（Golang）**：Kitex是Golang的RPC框架，专注于构建高效的远程过程调用系统，可优化网络通信、提升性能；Hertz作为Golang的HTTP框架，能快速搭建HTTP服务，在处理HTTP请求、路由管理等方面具备优势，满足不同场景下服务开发需求。
    - **Volo（Rust）**：是Rust语言的RPC框架，借助Rust语言在内存管理、性能优化方面的特性，为RPC开发提供高效且安全的解决方案。
2. **编解码器（CODEC）**
    - **多种序列化与反序列化工具**：Frugal、Fastpb、Sonic JSON、Pilota、Dynamic Thrift、Protobuf以及Thrift & Protobuf等编解码器，在不同场景下各有优势。如Sonic JSON适用于处理JSON格式数据的快速序列化与反序列化；Protobuf以高效的二进制编码，在对性能和数据大小要求苛刻的场景表现出色。
3. **网络库与运行时（Network Lib & Runtime）**
    - **Netpoll**：聚焦于RPC场景的网络框架，针对RPC通信特点进行优化，能高效处理网络连接、数据传输等操作，提升RPC系统的网络性能。
    - **Shmipc**：基于共享内存的进程间通信库，利用共享内存的特性，减少进程间数据传输开销，提高进程间通信效率。
    - **Monoio**：基于io -uring的异步运行时，充分利用io -uring的高效异步I/O能力，实现高性能的异步操作，提升系统整体的并发处理能力。
4. **工具（Tool）**
    - **Thriftgo与cwgo**：Thriftgo是Golang的Thrift代码生成工具，能根据Thrift定义文件自动生成Golang代码，提高开发效率；cwgo是一体化代码生成工具，可整合多种代码生成功能，一站式满足开发过程中的代码生成需求。
    - **Dynamicgo与Motore**：Dynamicgo和Motore可动态、高效地操作RPC数据，在运行时灵活处理RPC数据，提升系统的适应性和性能。
5. **中间件（Middleware）**：基于GAT（Generic Associated Types）和TAIT（Type -Aware Intersection Types）实现的异步中间件抽象，提供了一种灵活的方式来添加功能，如日志记录、权限验证、性能监控等，增强系统的扩展性和可维护性。 

![image-20250122221844786](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/image-20250122221844786.png)

`Gomall`项目使用`cloudwego`实现一个微服务架构的抖音电商，各个服务之间使用RPC进行调用

# 环境搭建

`gomall`项目的文件放在目录`~/projects/gomall`

## 环境以及插件

视频中罗列了需要使用的插件，但是我暂时没有考虑全部都装上。如下：

- `Go + Golang Tools`
- `Docker`
- `MySQL`
- `Material Icon Theme`
- `YAML`
- `vscode-proto3`
- `Makefile tools`

`Oh My Zsh`（一个shell的色彩高亮工具）

- `zsh-syntax-hightlightubg`
- `zsh-autosuggestions`

## 参考链接

![参考链接](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/image-20250122224555728.png)

## Hertz快速开始

正常编写一个Go项目的流程是要使用`go mod init`初始化mod，然后编写代码的同时使用`go mod tidy`来拉取依赖，这里就暂时忽略这步。

尝试使用Hertz启动一个打印"hello world"的服务，在`main.go`中敲入下述代码即可。简单来讲思路就是定义引擎、定义路由和最后启动引擎。

最终只要运行`go run main.go`就能跑起来，因为这是一个入门demo，只有一个文件，后续可能得加吧。服务跑起来后，根据提示打开对应端口的网页就能看到"hello world"。

```go
package main

import (
	"context"

	"github.com/cloudwego/hertz/pkg/app"
	"github.com/cloudwego/hertz/pkg/app/server"
	"github.com/cloudwego/hertz/pkg/protocol/consts"
)

func main() {
	h := server.Default()//使用默认引擎

	h.GET("/hello", func(ctx context.Context, c *app.RequestContext) {
		c.Data(consts.StatusOK, consts.MIMETextPlain, []byte("hello world"))
	})//定义"/hello"的Get请求以及路由函数

	h.Spin()//启动引擎
}
```

# 脚手架搭建

脚手架（Scaffolding）是一种为了加快软件开发过程而搭建的**基础架构或框架**，它为开发者提供了一个可扩展的基础，通常包含了项目的基本结构、配置文件、一些通用的工具和脚本等，类似于建筑中的脚手架为施工提供支撑和便利一样，软件开发中的脚手架为开发者提供了一个快速开始和构建项目的基础。

**在cloudwego中使用cwgo来根据IDL生成代码**

## IDL接口定义语言

IDL接口定义语言（Interface Definition Language），是一种用来描述软件组件或系统之间**接口**的语言。它**独立**于任何特定的编程语言和操作系统，用于精确地定义接口的功能、输入输出参数、消息格式等，使得不同的开发团队或不同的软件模块能够基于这个统一的接口定义进行开发和集成，常见的有 CORBA IDL、IDL for gRPC 等。

IDL的作用：

- **标准化、一致化接口定义**
- **跨语言支持**，IDL编写的接口可以便捷转化
- **版本控制和兼容性**
- **简化开发流程**，自动生成序列化和反序列化，减少开发工作量

视频主要介绍了Thrift和[`Protobuf`](https://protobuf.dev/programming-guides/proto3/)

## Thrift架构

https://diwakergupta.github.io/thrift-missing-guide/

https://thrift.apache.org/docs/idl

### thrift示例

```thrift
// idl/echo.thrift
namespace go api

struct Requeset {
    1: string message
}

struct Response {
    1: string message
}

service Echo{
    Response echo(1: Requeset res)
}
```

### 安装脚手架

运行命令直接`cloudwego`脚手架

```powershell
go install github.com/cloudwego/cwgo@latest
go install github.com/cloudwego/thriftgo@latest
```

查询[文章](https://www.cloudwego.io/zh/docs/cwgo/tutorials/auto-completion/)得到临时支持`cwgo`在bash下的补全

```bash
mkdir autocomplete # You can choose any location you like
cwgo completion bash > ./autocomplete/bash_autocomplete
source ./autocomplete/bash_autocomplete
```

在`gomall`目录生成文件夹`demo/demo_thrift`

```
mkdir demo/demo_thrift
```

在`gomall/demo/demo_thrift`目录生成结构代码到`gomall/demo/demo_thrift`

```powershell
cwgo server --type RPC --module gomall/demo/demo_thrift --service demo_thrift --idl ../../idl/echo.thrift
```

生成后修改gomall/demo/demo_thrift/biz/service/echo.go，补全run逻辑

```go
// Run create note info
func (s *EchoService) Run(req *api.Requeset) (resp *api.Response, err error) {
	// Finish your business logic.

	return &api.Response{Message: req.Message}, nil
}
```

在`demo_thrift`目录下执行`go mod tidy`补全依赖，然后执行`go run .`顺利启动，结果如下：

```powershell
&{Env:test Kitex:{Service:demo_thrift Address::8888 LogLevel:info LogFileName:log/kitex.log LogMaxSize:10 LogMaxBackups:50 LogMaxAge:3} MySQL:{DSN:gorm:gorm@tcp(127.0.0.1:3306)/gorm?charset=utf8mb4&parseTime=True&loc=Local} Redis:{Address:127.0.0.1:6379 Username: Password: DB:0} Registry:{RegistryAddress:[127.0.0.1:2379] Username: Password:}}
```

## Protobuf

https://protobuf.dev/programming-guides/proto3/

### protobuf示例

```protobuf
// idl/echo.proto
syntax = "proto3";

package pbapi;

option go_package = "/pbapi";

message Request {
  string message = 1;
}

message Response {
  string message = 1;
}

service EchoService {
  rpc Echo (Request) returns (Response) {}
}
```

### 安装脚手架

根据[github链接](https://github.com/protocolbuffers/protobuf/releases)下载`protobuf`的release版本。

同时，windows上使用`protobuf`需要配置环境变量来使用，参考文章：https://developer.aliyun.com/article/797456

Linux上将文件解压移动到具体目录，

1. 在bin目录下将可执行文件拷贝到系统bin包下，授予执行权限

   ```
   sudo cp protoc /usr/local/bin
   sudo chmod +x /usr/local/bin/protoc
   ```

2. 在include目录下将文件夹拷贝到系统include下

   ```
   sudo cp -a google /usr/local/include
   ```

3. 验证protoc

   ```
   protoc --version
   ```

   得到`libprotoc 25.6`表示安装成功

创建文件夹，并生成代码结构

```bash
xwq@xwq-virtual-machine:~/gomall$ mkdir demo/demo_proto
xwq@xwq-virtual-machine:~/gomall$ cd demo/demo_proto/
xwq@xwq-virtual-machine:~/gomall/demo/demo_proto$ cwgo server -I ../../idl --type RPC --module gomall/demo/demo_proto --service demo_proto --idl ../../idl/echo.proto
```

同样修改生成后修改gomall/demo/demo_thrift/biz/service/echo.go，补全run逻辑

```go
// Run create note info
func (s *EchoService) Run(req *api.Requeset) (resp *api.Response, err error) {
	// Finish your business logic.

	return &api.Response{Message: req.Message}, nil
}
```

在`demo_proto`目录下执行`go mod tidy`补全依赖，然后执行`go run .`顺利启动，结果如下：

```powershell
&{Env:test Kitex:{Service:demo_proto Address::8888 LogLevel:info LogFileName:log/kitex.log LogMaxSize:10 LogMaxBackups:50 LogMaxAge:3} MySQL:{DSN:gorm:gorm@tcp(127.0.0.1:3306)/gorm?charset=utf8mb4&parseTime=True&loc=Local} Redis:{Address:127.0.0.1:6379 Username: Password: DB:0} Registry:{RegistryAddress:[127.0.0.1:2379] Username: Password:}}
```

## Makefile编写

Makefile的编写是为了简化操作，一键执行命令。在gomall目录下新建Makefile，代码如下：

```makefile
.PHONY: gen-demo-proto
gen-demo-proto:
	@cd demo/demo_proto && cwgo server -I ../../idl --type RPC --module gomall/demo/demo_proto --service demo_proto --idl ../../idl/echo.proto

.PHONY: gen-demo-thrift
gen-demo-thrift:
	@cd demo_demo_thrift && cwgo server --type RPC --module gomall/demo/demo_thrift --service demo_thrift --idl ../../idl/echo.thrift
```

## CloudeWego对IDL的扩展

https://www.cloudwego.io/docs/hertz/tutorials/toolkit/annotation

一些注解，有空看看

# 服务注册与服务发现

## 为什么要有服务注册与服务发现？

微服务的拆分是为了使得各个服务之间相互解耦合，避免一个服务崩溃后所有服务都崩溃，也就是为了避免单点故障。同时，在微服务中为了提高一组服务的性能，一组服务是采用分布式部署的，即分布在多台服务器上的，为了提高服务的应对能力，有时需要增减服务器，而增减服务器必然会带来ip的变化，为了减少人工介入手动更改配置，就不能写死代码。那就套一层来解决，使用一个服务注册中心，服务注册中心对外提供服务发现能力。

在微服务提出前，可以想到采用负载均衡器（LB）或者网关（Gateway）来实现，单独建立一个节点统一对外提供服务。所有的服务向C进行注册，C记录服务列表，当A发送请求到C时，C会代而选择一个服务，向该服务发送请求。

![image-20250125155216852](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/image-20250125155216852.png)

但是这样形成一个单点，如果这个节点崩溃了，整个系统就无法提供正常的访问行为了，因此需要将服务访问的功能向前迁移到请求发送方，A仅仅通过注册中心获取可用的服务列表，再通过负载均衡选择要访问的服务。C只起到存储的作用，这样就减轻了C的负载，减轻了单点故障的问题。

![image-20250125155104102](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/image-20250125155104102.png)

有很多中间件实现上述服务注册和服务发现功能，具体如何选择根据CAP原则和实际需求选用。

## consul

示例：以demo_proto改造服务注册功能，使用docker启动consul，编写客户端代码发现proto服务

cloudwego官网kitex参考：https://www.cloudwego.io/docs/kitex/tutorials/service-governance/service_discovery/consul/

### 改造服务注册

在`gomall/demo/demo_proto/main.go`中的`kitexInit()`函数中添加服务注册代码

```go
// register
r, err := consul.NewConsulRegister(conf.GetConf().Registry.RegistryAddress[0])
if err != nil {
	log.Fatal(err)
	return
}
opts = append(opts, server.WithRegistry(r))
```

需要自己手动添加一下依赖

```go
consul "github.com/kitex-contrib/registry-consul"
```

### docker compose启动consul

提前拉取镜像`hashicorp/consul`。这次用阿里云ACR做了仓库中介，先在win上拉取镜像，然后推送到ACR，再把仓库设置公开，按照ACR说明在虚拟机上拉取`consul`镜像。

编写`docker-compose.yaml`，使用`docker compose up -d`后台启动。

```yaml
version: '3'
services:
  consul:
    image: 'hashicorp/consul'
    ports:
      - 8500:8500
```

这里还要注意端口设置为了8500，要取修改`gomall/demo/demo_proto/conf/test/conf.yaml`下`registry_address`端口为8500

```yaml
registry:
  registry_address:
    - 127.0.0.1:8500
  username: ""
  password: ""
```

### 编写客户端代码发现proto服务

创建`cmd/client/main.go`，和官网示例还是冲突。很关键在于引入自定义的`demo_proto`下两个包，这是客户端和请求的定义。

```go
package main

import (
	"context"
	"fmt"
	"gomall/demo/demo_proto/kitex_gen/pbapi"
	"gomall/demo/demo_proto/kitex_gen/pbapi/echoservice"
	"log"

	"github.com/cloudwego/kitex/client"
	consul "github.com/kitex-contrib/registry-consul"
)

func main() {
	r, err := consul.NewConsulResolver("127.0.0.1:8500")
	if err != nil {
		log.Fatal(err)
	}
	c, err := echoservice.NewClient("demo_proto", client.WithResolver(r))
	if err != nil {
		log.Fatal(err)
	}
	res, err := c.Echo(context.TODO(), &pbapi.Request{Message: "hello,world!"})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(res)
}
```

# 配置管理

配置的读取：

- File Config：从文件读取配置，常见右YAML、JSON、TOML
- ENV Config：从环境变量读取配置
- Config Center：从配置中心读取配置

## File Config

某一个服务的配置最终都是要转换为一个结构体以供程序读取和使用的。

conf目录下conf.go负责解析配置，conf目录下有dev、online、test三个文件夹对应开发、生产、测试三种情况的yaml配置文件。conf.go的init逻辑很清晰，现根据环境变量GO_ENV尝试获取通过环境变量指定的配置读取模式（默认采用test），再去对应文件夹读取配置文件。

## ENV Config

- Linux env：`export APP_ENV=online`
- .env file：定义.env文件，使用相应的库去读取环境变量（下文展示）
- Docker env：设置dockers的环境变量
- k8s：略

下面是一个通过环境变量配置MySQL的例子：

先修改test目录下conf.yml，更改MySQL配置，使用占位符

```yaml
mysql:
  # dsn: "gorm:gorm@tcp(127.0.0.1:3306)/gorm?charset=utf8mb4&parseTime=True&loc=Local"
  dsn: "%s:%s@tcp(%s:3306)/%s?charset=utf8mb4&parseTime=True&loc=Local"
```

在`gomall/demo/demo_proto/biz/dal/mysql/init.go`这个初始化MySQL连接的地方，通过环境变量填充从配置文件读取的配置

```go
func Init() {
	dsn := fmt.Sprintf(conf.GetConf().MySQL.DSN,
		os.Getenv("MYSQL_USER"),
		os.Getenv("MYSQL_PASSWORD"),
		os.Getenv("MYSQL_HOST"),
		os.Getenv("MYSQL_DATABASE"),
	)
	DB, err = gorm.Open(mysql.Open(dsn),
		&gorm.Config{
			PrepareStmt:            true,
			SkipDefaultTransaction: true,
		},
	)
	if err != nil {
		panic(err)
	}
    // print MySQL Version
    type Version struct {
		Version string
	}
	var v Version

	err = DB.Raw("select version() as version").Scan(&v).Error
	fmt.Println(v)
}
```

我们可用通过Linux下的export命令来添加环境变量，例如

```bash
export MYSQL_USER=root
```

也可以选择`.env`的方式进行配置。先在demo_proto下编写.env，例如

```bash
"MYSQL_USER"=root
"MYSQL_PASSWORD"=root
"MYSQL_HOST"=localhost
"MYSQL_DATABASE"=test
```

使用`godetenv`库来加载.env，先在demo_proto下安装库

```
~/gomall/demo/demo_proto$ go get github.com/joho/godotenv
```

在项目启动的时候调用`godetenv`库来加载.env，在main中添加代码

```go
err := godotenv.Load()
	if err != nil {
		panic(err)
	}
	dal.Init()
```

在docker-compose.yml中添加MySQL容器

```yaml
mysql:
    image: 'mysql'
    ports:
      - 3306:3306
    enviroment:
       MYSQL_ROOT_PASSWORD: root  
       MYSQL_DATABASE: test
```

## Config Center

仓库参考：https://github.com/orgs/kitex-contrib/repositories

# ORM

## 标准库访问

https://golang.google.cn/doc/tutorial/database-access

## GORM

官网好用撒

## 环境改造和确认

修改类docker-compose.yml和.env的数据库为demo_proto

安装数据库可视化插件

![image-20250125222551979](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/image-20250125222551979.png)

## 创建数据模型

```
package model

import "gorm.io/gorm"

type User struct {
	gorm.Model
	Email    string `gorm:"uniqueIndex;type:varchar(64) not null"`
	Password string `gorm:"type:varchar(64) not null"`
}

// 指定表名
func (User) TableName() string {
	return "user"
}
```

初始化连接后，可用自动迁移建表

```
DB.AutoMigrate(&model.User{})
```

## CRUD

比较简单

```go
package main

import (
	"fmt"
	"gomall/demo/demo_proto/biz/dal"
	"gomall/demo/demo_proto/biz/dal/mysql"
	"gomall/demo/demo_proto/biz/model"

	"github.com/joho/godotenv"
)

func main() {
	err := godotenv.Load()
	if err != nil {
		panic(err)
	}
	dal.Init()

	// mysql.DB.Create(&model.User{Email: "demo@example.com", Password: "demo"})
	mysql.DB.Model(&model.User{}).Where("email = ?", "demo@example.com").Update("password", "21222")
	var row model.User
	mysql.DB.Model(&model.User{}).Where("email = ?", "demo@example.com").First(&row)
	fmt.Printf("row: %+v\n", row)
	mysql.DB.Where("email = ?", "demo@example.com").Delete(&model.User{})
	//强制删除测试
	mysql.DB.Unscoped().Where("email = ?", "demo@example.com").First(&row)
}
```

# 编码指南

- Code style
- Custom Error Codes
- Log style：结构化日志+关键信息+结合链路追踪+稳定性
- Conventional Commits
- Semantic Versioning

## 代码风格

uber-go风格：https://github.com/uber-go/guide/blob/master/style.md#introduction

protobuf的约定：https://protobuf.dev/programming-guides/style/

## 日志风格

hertz适配日志库：https://github.com/hertz-contrib/logger

## 提交规范

约定式提交：https://www.conventionalcommits.org/en/v1.0.0/

## 语义版本控制

https://semver.org/

# 微服务通信

- RPC
- RESTful API
- Message Middleware

## RPC

- Thrift
- gRPC

### Thrift的RPC调用

一次RPC调用的demo

```go
// demo_thrift/cmd/client.go
package main

import (
	"context"
	"fmt"
	"gomall/demo/demo_thrift/kitex_gen/api"
	"gomall/demo/demo_thrift/kitex_gen/api/echo"

	"github.com/cloudwego/kitex/client"
)

func main() {
	cli, err := echo.NewClient("demo_thrift", client.WithHostPorts("localhost:8888"))
	if err != nil {
		panic(err)
	}

	res, err := cli.Echo(context.Background(), &api.Requeset{
		Message: "hello",
	})
	if err != nil {
		fmt.Println(err)
	}
	fmt.Printf("%v", res)
}
```

传递RPC info的方法

demo_thrift/biz/service/echo.go

```go
// Run create note info
func (s *EchoService) Run(req *api.Requeset) (resp *api.Response, err error) {
	// Finish your business logic.
	info := rpcinfo.GetRPCInfo(s.ctx)
	fmt.Println(info.From().ServiceName())

	return &api.Response{Message: req.Message}, nil
}
```

在gomall/demo/demo_thrift/cmd/client/clinet.go的main最前面添加

```go
cli, err := echo.NewClient("demo_thrift", client.WithHostPorts("localhost:8888"),
		client.WithMetaHandler(transmeta.ClientTTHeaderHandler),
		client.WithTransportProtocol(transport.TTHeader),
		client.WithClientBasicInfo(&rpcinfo.EndpointBasicInfo{
			ServiceName: "demo_thrift",
		}),
	)
```

rpcinfo和其他元信息传递，meainfo实现信息传递。kitex的gRPC需要满足CGI网关风格的key（大写+下划线格式）

### gRPC调用

echo.go

```
// Run create note info
func (s *EchoService) Run(req *pbapi.Request) (resp *pbapi.Response, err error) {
	// Finish your business logic.
	clinetName, ok := metainfo.GetPersistentValue(s.ctx, "CLIENT_NAME")
	fmt.Println(clinetName, ok)
	return &pbapi.Response{Message: req.Message}, nil
}
```

client.go

```
func main() {
	r, err := consul.NewConsulResolver("127.0.0.1:8500")
	if err != nil {
		log.Fatal(err)
	}
	c, err := echoservice.NewClient("demo_proto", client.WithResolver(r),
		client.WithTransportProtocol(transport.GRPC),
		client.WithMetaHandler(transmeta.ClientHTTP2Handler),
	)
	if err != nil {
		log.Fatal(err)
	}
	ctx := metainfo.WithPersistentValue(context.Background(), "CLIENT_NAME", "demo_proto_client")
	res, err := c.Echo(ctx, &pbapi.Request{Message: "hello,world!"})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(res)
}
```

- 设置值`metainfo.WithPersistentValue`和`metainfo.WithValue`区别在于能否持续传递，`WithValue`只传递到下一次，`Persist`是持续
- 获取值对应`getValue`和`getPersistentValue`

错误信息传递：

改造服务端echo.go

```go
// Run create note info
func (s *EchoService) Run(req *pbapi.Request) (resp *pbapi.Response, err error) {
	// Finish your business logic.
	clinetName, ok := metainfo.GetPersistentValue(s.ctx, "CLIENT_NAME")
	fmt.Println(clinetName, ok)
	if req.Message == "error" {
		return nil, kerrors.NewGRPCBizStatusError(1004001, "client param error")
	}
	return &pbapi.Response{Message: req.Message}, nil
}
```

改造客户端client.go

```go
ctx := metainfo.WithPersistentValue(context.Background(), "CLIENT_NAME", "demo_proto_client")
res, err := c.Echo(ctx, &pbapi.Request{Message: "error"})
var bizErr *kerrors.GRPCBizStatusError
if err != nil {
	ok := errors.As(err, &bizErr)
	if ok {
		fmt.Printf("%#v", bizErr)
	}
	klog.Fatal(err)
}
```

## 中间件

参考官网给出kitex支持中间件：https://github.com/kitex-contrib，当然也有hertz参考：https://github.com/hertz-contrib

新建middleware/middleware.go

```
package middleware

import (
	"context"
	"fmt"
	"time"

	"github.com/cloudwego/kitex/pkg/endpoint"
)

func Middleware(next endpoint.Endpoint) endpoint.Endpoint {
	return func(ctx context.Context, req, resp interface{}) (err error) {
		begin := time.Now()
		err = next(ctx, req, resp)
		fmt.Println(time.Since(begin))
		return err
	}
}
```

在服务端main.go引入中间件

```
opts = append(opts, server.WithServiceAddr(addr),server.WithMiddleware(middleware.Middleware))
```

在客户端client.go引入中间件

```
c, err := echoservice.NewClient("demo_proto", client.WithResolver(r),
		client.WithTransportProtocol(transport.GRPC),
		client.WithMetaHandler(transmeta.ClientHTTP2Handler),
		client.WithMiddleware(middleware.Middleware),
	)
```

## RESTful API

cloudwego下找example：https://github.com/cloudwego

cloudwego hertz example：https://github.com/cloudwego/hertz-examples

hertz中间件参考：https://github.com/hertz-contrib

# 前端页面

- vue/react/angular
- Bootstrap
- Fontawesome
- go template

## 工具准备

添加proto文件后后hertz代码生成：https://www.cloudwego.io/docs/hertz/tutorials/toolkit/usage-protobuf/，这里仅仅是利用代码生成功能生成代码结构，后续修改了原先的API定义

```
xwq@xwq-virtual-machine:~/gomall$ cd app/frontend/
xwq@xwq-virtual-machine:~/gomall/app/frontend$ cwgo server --type HTTP --idl ../../idl/frontend/home.proto --service frontend -module gomall/app/frontend -I ../../idl
```

hertz渲染HTML的配置：https://www.cloudwego.io/zh/docs/hertz/tutorials/basic-feature/render/#html

air一个Go即时加载工具：https://github.com/air-verse/air

bootstrap下载：https://getbootstrap.com/docs/5.3/getting-started/download/，只拷贝bootstrap.bundle.min.js和bootstrap.min.css两个文件到static下js和css目录

## go template

main.go添加代码加载static和tmpl

```go
h.LoadHTMLGlob("template/*")
	//h.LoadHTMLFiles("render/html/index.tmpl")
	h.Static("/static", "./")
	h.Spin()
```

直接从组件库摘自己想要的效果组成界面

go template抽象公共部分，直接抄了仓库代码。官网参考：https://pkg.go.dev/text/template

### 后端渲染数据到tmpl

service/home.go写死业务逻辑，提供数据

```go
func (h *HomeService) Run(req *home.Empty) (map[string]any, error) {
	//defer func() {
	// hlog.CtxInfof(h.Context, "req = %+v", req)
	// hlog.CtxInfof(h.Context, "resp = %+v", resp)
	//}()
	// todo edit your code
	var resp = make(map[string]any)
	items := []map[string]any{
		{"Name": "T-shirt-1", "Price": 100, "Picture": "/static/image/t-shirt-1.jpeg"},
		{"Name": "T-shirt-2", "Price": 110, "Picture": "/static/image/t-shirt-1.jpeg"},
		{"Name": "T-shirt-3", "Price": 120, "Picture": "/static/image/t-shirt-2.jpeg"},
		{"Name": "T-shirt-4", "Price": 130, "Picture": "/static/image/notebook.jpeg"},
		{"Name": "T-shirt-5", "Price": 140, "Picture": "/static/image/t-shirt-1.jpeg"},
		{"Name": "T-shirt-6", "Price": 150, "Picture": "/static/image/t-shirt.jpeg"},
	}
	resp["Title"] = "Hot Sales"
	resp["Items"] = items
	return resp, nil
}
```

app/frontend/biz/handler/home/home_service.go是逻辑处理函数，此处将从home.go得到的数据渲染到tmpl（如下代码），并返回HTML。整个调用链是router->handler->service

```
c.HTML(consts.StatusOK, "home.tmpl", resp)
```

# 用户服务

## 身份管理

- identification：认证，如何确认身份
- Authorization：授权
- Authentication：鉴权
- Permission control：权限管理

## Hertz身份认证中间件

- [hertz-contrib/sessions](https://www.cloudwego.io/zh/docs/hertz/tutorials/basic-feature/middleware/session/)
- [hertz-contrib/jwt](https://www.cloudwego.io/zh/docs/hertz/tutorials/basic-feature/middleware/jwt/)
- [hertz-contrib/paseto](https://www.cloudwego.io/zh/docs/hertz/tutorials/basic-feature/middleware/paseto/)：比jwt更安全昂
- [hertz-contrib/keyauth](https://www.cloudwego.io/zh/docs/hertz/tutorials/basic-feature/middleware/keyauth/)
