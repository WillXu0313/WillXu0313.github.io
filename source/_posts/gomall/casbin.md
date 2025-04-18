---
title: casbin
date: 2025-04-19 07:04:02
categories:
- goMall
---

# RBAC——基于角色权限的模型

参考文章：

https://blog.csdn.net/m0_62006803/article/details/133962328

https://www.zhihu.com/question/316238486

## RBAC是什么？

Role-Based Access Control，基于角色的访问控制。这是一种广泛应用于计算机系统和网络安全领域的访问控制模型。

RBAC模型认为授权实际上是Who对What进行How的操作，是Who、What、How的三元组关系。

**Who：是权限的拥有者或主体（如：User，Role）。**

**What：是操作或对象（operation，object）。**

**How：具体的权限（Privilege,正向授权与负向授权）**

（在阿里云进行操作的时候可以很明显看出这种模型的使用）

**权限**分配给➡**角色**，再将**角色**分配给➡**用户**，很经典也很好理解，它们是**多对多**的关系——一个用户可以被分配多个角色，一个角色可以被多个用户所拥有；一个角色也可以被分配多个权限，同一个权限可以被分配给多个角色。核心概念：

1. 权限（Permission）：权限是指对系统资源进行操作的许可，如读取、写入、修改等。权限可以被分配给角色。
2. 角色（Role）：角色是指在系统中具有一组相关权限的抽象概念，代表了用户在特定上下文中的身份或职能，例如管理员、普通用户等。
3. 用户（User）：用户是指系统的实际使用者，每个用户可以被分配一个或多个角色。

4. 分配（Assignment）：分配是指将角色与用户关联起来，以赋予用户相应的权限。
5. 用户组：用户组是用户的集合，同一个用户组拥有相同的角色属性，有相同的权限。

重点解释一下用户组——**之所以引入用户组是为了减少对每个用户逐个分配角色的次数**。引入用户组后，每个用户的权限应该等于用户个人权限加上用户组权限了，基本属性加上特殊属性啦。

> 举例：销售中心的员工都有销售员的基本角色，对销售中心的每个员工逐个分配销售员这个角色实在是太麻烦了。
>
> 将销售中的所有员工都加到一个销售中心的用户组中，给销售中心这个用户组赋予销售员的基本角色，这样销售中心的所有员工就拥有了销售员的基本角色，拥有了对应的权限，避免了手动逐个授权的麻烦事。

看评论区理解了一下用户组：https://www.zhihu.com/question/316238486

## RBAC怎么用？

理解了上述的核心概念，接下来应该关心RBAC的权限管理具体是如何实现的——具体的访问控制流程？数据库的库表设计？以及casbin怎么用起来这一套的？

# Casbin开源访问控制框架

## 快速开始

新建一个rbac_model.conf文件

```
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
```

新建一个main.go文件

```go
package main

import (
	"fmt"
	"github.com/casbin/casbin/v2"
	"github.com/casbin/casbin/v2/model"
)

func main() {
	// 加载model文件
	m, err := model.NewModelFromFile("rbac_model.conf")
	if err != nil {
		panic(err)
	}

	// 使用默认适配器初始化Enforcer
	e, err := casbin.NewEnforcer(m)
	if err != nil {
		panic(err)
	}

	// 设置Policy，可以通过文件或者直接编程设置
	// 示例：添加一些策略
	e.AddPolicy("admin", "data1", "read")
	e.AddGroupingPolicy("alice", "admin")

	// 验证权限
	sub := "alice" // 用户
	obj := "data1" // 资源
	act := "read"  // 动作

	ok, err := e.Enforce(sub, obj, act)
	if err != nil {
		panic(err)
	}
	if ok {
		fmt.Println("允许访问")
	} else {
		fmt.Println("拒绝访问")
	}
}
```

## 工作原理

https://v1.casbin.org/docs/en/how-it-works

先理解conf文件的配置。

先理解几个名词——sub、obj、act、eft。主体通过访问方法获取资源？（这蹩脚的翻译）

- sub (subject)：主体
- obj (object)：资源
- act (action)：访问方法
- eft (effect)：策略执行的结果，默认为allow

Casbin的访问控制模型被抽象为基于 **PERM (Policy, Effect, Request, Matcher)** 的一个配置文件。

### Request

定义请求参数，基本长这样：`r={sub,obj,act}`

### Policy

定义访问的具体规则的形式，后续在代码里添加具体的规则，基本长这样：`p={sub, obj, act}`or`p={sub, obj, act, eft}`.

**Note:** If eft (policy result) is not defined, then the result field in the policy file will not be read, and the matching policy result will be allowed by default.

即在policy不定义eft参数的话，eft默认为allow。

### Matcher

匹配请求和政策的规则，检查匹配情况，返回Policy执行的结果

例子`m = r.sub == p.sub && r.act == p.act && r.obj == p.obj`说明只要Request和Policy参数匹配，就会返回`p.eft`，即将匹配结果存放在`p.eft`中

### Effect

对匹配结果再次作出逻辑组合判断。

例子`e = some(where(p.eft == allow))`说明只要有匹配结果是allow的，最终结果就是true。

例子`e = some(where (p.eft == allow)) && !some(where (p.eft == deny))`说明匹配结果全是allow并且没有是deny，最终结果才是true

### 添加策略与验证权限

```
// 设置Policy，可以通过文件或者直接编程设置
	// 示例：添加一些策略
	e.AddPolicy("admin", "data1", "read")
	e.AddGroupingPolicy("alice", "admin")

	// 验证权限
	sub := "alice" // 用户
	obj := "data1" // 资源
	act := "read"  // 动作

	ok, err := e.Enforce(sub, obj, act)
	if err != nil {
		panic(err)
	}
	if ok {
		fmt.Println("允许访问")
	} else {
		fmt.Println("拒绝访问")
	}
```

## RBAC角色控制

https://v1.casbin.org/docs/zh-CN/rbac

### g的使用

字符串记录用户、角色，只是记录了**映射**关系，表示继承关系——因此用户、角色的命名要区分，用role_xxx进行区分。

g其实表示的是group，下面这种形式定义了前者**继承**后者。在实际的应用中，g的定义前者表示用户，后者表示用户组；g2的定义前者是用户，后者是用户组。两者是两个RBAC系统。

```
[role_definition]
g = _, _
g2 = _, _
```

g判断用户是否属于某个角色，g的定义说明了用户和角色之间的组关系，即一个用户是否属于某个角色组之下

其实这样做确实简化了管理上的繁琐，但是对软件设计的要求也更高了，需要自行对用户、角色负责。

用户和角色的关系，当前版本可以无限传递下去——假设`A`具有角色 `B`，`B` 具有角色 `C`，那么 `A` 具有角色 `C`

验证有效性要鉴权！casbin只是控制访问（可不可以访问），没法验证用户、角色的有效性

自己在代码里面试了下，确实will有访问权限。

```
	e.AddPolicy("admin", "data1", "read")
	e.AddGroupingPolicy("alice", "admin")
	e.AddGroupingPolicy("will", "alice")

	// 验证权限
	sub := "will"  // 用户
	obj := "data1" // 资源
	act := "read"  // 动作
```

官网文档提供了基础的RBAC模型、基于用户组RBAC模型的conf文件

角色可以具备层次结构：https://v1.casbin.org/docs/zh-CN/rbac#%E8%A7%92%E8%89%B2%E5%B1%82%E6%AC%A1



# 全都是问题



没时间纠结原理了，先看casbin怎么用的，快速搭建起基础的RBAC服务吧。。。

看了下架构，发现不知道代码写在哪，糟了。

wire依赖注入要用，得认真学

casbin建立的授权要访问数据库吧，咋个整好的



综上，先整个casbin的demo玩玩明白

看官方文档看不进去，光看理论也烦，动手实践又不搞。。。动手玩起来-分解问题的能力啊动手的能力啊

美学东dpolicy的配置以及matcher的一些函数在model中的配置

主要关注casbin在入库上的设计，更多在库表设计上