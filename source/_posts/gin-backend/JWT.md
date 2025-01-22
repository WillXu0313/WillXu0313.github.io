---
title: JWT的Go语言实践
date: 2025-01-22 11:25:00
categories:
- bluebell
---
# JWT

参考：[在gin框架中使用JWT | 李文周的博客 (liwenzhou.com)](https://www.liwenzhou.com/posts/Go/jwt_in_gin/)

## 原理

## Go实践

Go语言中直接使用jwt-go库来实现生成JWT和解析JWT的功能。

### 定制声明

我不知道为什么这个地方要叫做Claims，其实对应原理的Payload（负载）。jwt官方标准的负载封装为`jwt.StandardClaims`，我们将其嵌入到自定义的结构体中，形成自定义的Claims——

```go
// 自定义负载声明部分
type MyClaims struct {
	Username string `json:"username"`
	jwt.StandardClaims
}
```

一些必要的参数，如过期时间和密钥

```go
// 设置过期时间
const TokenExpireDurTion = time.Hour * 2

// 密钥，用于生成签名和解析token
var MySecret = []byte("我就是我")
```

### 生成JWT

关键步骤：

- `jwt.NewWithClaims(jwt.SigningMethodHS256, c)`使用指定签名方法（jwt.SigningMethodHS256）和负载（c）来创建签名对象
- `token.SignedString(MySecret)`根据密钥和签名对象（头部和负载之和）生成签名，返回完整的编码为字符串形式的token。

```go
// 生成JWT
func GenToken(username string) (string, error) {
	//创建声明
	c := &MyClaims{
		username,
		jwt.StandardClaims{
			ExpiresAt: time.Now().Add(TokenExpireDurTion).Unix(),
			Issuer:    "WiilXu",
		},
	}
	// fmt.Println("c:", *c)
	//使用指定签名方法来创建签名对象,包含了头部和负载了，就差签名
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, c)
	fmt.Println("GenToken-token:", token)
	//使用密钥生成签名并获得完整的编码后的token
	return token.SignedString(MySecret)
}
```

### 解析JWT

关键步骤：

- `jwt.ParseWithClaims(tokenString, &MyClaims{},func(t *jwt.Token) (interface{}, error) { return MySecret, nil })`使用`jwt.ParseWithClaims`将JWT从字符串形式解析为可读的token，它的原型如下：

  ```go
  func jwt.ParseWithClaims(tokenString string, claims jwt.Claims, keyFunc jwt.Keyfunc) (*jwt.Token, error)
  ```

  三个关键参数对应 字符串token、claims、keyfunc返回密钥，它会返回解析后的token。

- `token.Claims.(*MyClaims)`是类型断言，将token的Claims转换为我们定义的类型，就可以自己使用了。

```go
// 解析JWT
func ParseToken(tokenString string) (*MyClaims, error) {
	//将JWT从字符串形式解析为可读的token
	token, err := jwt.ParseWithClaims(tokenString, &MyClaims{},
		func(t *jwt.Token) (interface{}, error) { return MySecret, nil })
	if err != nil {
		return nil, err
	}
	//将claims（负载部分内容）从token中读出
	if claims, ok := token.Claims.(*MyClaims); ok {
		return claims, nil
	}
	return nil, errors.New("invalid token")
}
```

### 验证

main函数验证上述生成和解析是正确的。

```go
func main() {
	// 生成token
	var username string = "Xu"
	token, err := GenToken(username)
	fmt.Println("token:", token)
	if err != nil {
		fmt.Println(err)
		return
	}
	// 解析token
	c, err := ParseToken(token)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println("c:", c)
}
```

## GIN使用

注册一条专门的路由用来对外提供获取Token。这里的Token其实是Access Token，和后续的ReFresh Token不同， 是用户请求携带Access Token发往其他接口，因此需要检验Token的中间件。

### 提供Token

编写路由

```go
r.POST("/auth", authHandler)
```

编写路由响应函数，正确流程：解析参数->鉴权成功->发放token

```go
func authHandler(c *gin.Context) {
	//解析参数
	var user UserInfo
	err := c.ShouldBind(&user)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{
			"code": 2001,
			"msg":  "无效的参数",
		})
		return
	}
	//校验参数（鉴权），正确发放token，不正确返回鉴权失败
	if user.UserName == "Xu" && user.Password == "1" {
		//生成token
		tokenString, _ := GenToken(user.UserName)
		c.JSON(http.StatusOK, gin.H{
			"code": 2000,
			"msg":  "success",
			"data": gin.H{"token": tokenString},
		})
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"code": 2002,
		"msg":  "鉴权失败",
	})
}
```

### 解析Token

客户端携带Token有三种方式 1.放在请求头 2.放在请求体 3.放在URI。这里假设Token放在Header的Authorization中，并使用Bearer开头，具体实现方式要依据你的实际业务情况决定。

解析Token的是中间件。正确流程：获取参数->获取tokenString->检查参数并进一步处理

```go
func JWTAuthMiddleware() func(c *gin.Context) {
	return func(c *gin.Context) {
		//获取Authorization
		authHeader := c.Request.Header.Get("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusOK, gin.H{
				"code": 2003,
				"msg":  "请求头中auth为空",
			})
			c.Abort()
			return
		}
		//检查格式
		parts := strings.SplitN(authHeader, " ", 2)
		if !(len(parts) == 2 && parts[0] == "Bearer") {
			c.JSON(http.StatusOK, gin.H{
				"code": 2004,
				"msg":  "请求头中auth格式有误",
			})
			c.Abort()
			return
		}

		//获取tokenString
		mc, err := ParseToken(parts[1])
		if err != nil {
			c.JSON(http.StatusOK, gin.H{
				"code": 2005,
				"msg":  "无效的Token",
			})
			c.Abort()
			return
		}
		//将当前请求的username信息保存到请求的上下文c上
		c.Set("username", mc.Username)
		c.Next() // 后续的处理函数可以用过c.Get("username")来获取当前请求的用户信息
	}
}
```

### 验证

为路径`/home`注册中间件`JWTAuthMiddleware()`来验证JWT的可行性。

```
r.GET("/home", JWTAuthMiddleware(), homeHandler)

func homeHandler(c *gin.Context) {
	username := c.MustGet("username").(string)
	c.JSON(http.StatusOK, gin.H{
		"code": 2000,
		"msg":  "success",
		"data": gin.H{"username": username},
	})
}
```

具体验证过程：

1. 向`/auth`发送POST请求获取token
2. 将token放入`Authorization`，向`/home`发送GET请求

### 调包

如果不想自己实现上述功能，你也可以使用Github上别人封装好的包，比如https://github.com/appleboy/gin-jwt