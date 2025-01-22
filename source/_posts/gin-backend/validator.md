---
title: validator使用
date: 2025-01-22 11:25:00
categories:
- bluebell
---
# validator

[validator库参数校验若干实用技巧 | 李文周的博客 (liwenzhou.com)](https://www.liwenzhou.com/posts/Go/validator-usages/)

## 概述

validator是Go语言社区中开源的数据验证的工具包，Gin框架使用这个包进行数据验证。

## 作用

总的来说，`validator`包为 Go 语言开发者提供了一种方便、灵活且强大的方式来进行数据验证，有助于提高代码的可靠性和健壮性，减少因数据不合法而导致的错误和异常。

### 结构体字段验证（基础校验）

1. **基础校验**：对单个字段或变量应用简单的验证规则，例如验证是否为必填、是否为合法的电子邮件、字符串长度、整数范围等，是使用tag（标签）来实现的（即结构体字段后的`中的文字）
2. 结构体嵌套验证，当一个结构体包含其他结构体作为字段时，可以同时对嵌套的结构体进行验证

### 自定义验证函数（自定义复合校验）

1. 自定义**复合校验**：校验有复杂的逻辑，适用于动态校验和或多个字段之间的复杂关系。validator对于一些简单的符合校验有预置规则，比如确认密码和密码要相同用`eqfield`标签，但更复杂一些的校验则需要自定义验证函数来进行验证。自定义校验函数需要通过`validate.RegisterStructValidation()` 注册
2. 可灵活拓展，进行复杂的业务逻辑规则的检验

### 错误处理和返回

1. 当验证失败时，会返回详细的错误信息，指出哪个字段违反了哪个验证规则。
2. 易于集成

## 使用

基础校验：打tag就能自己校验了。复合校验：自定义校验方法。

### 快速上手

下面是官网的上手介绍，经典使用方式——在err不为nil时，进行err.(validator.ValidationErrors) 的类型断言，再遍历获取具体的错误信息。

```go
package main

import (
	"fmt"

	"github.com/go-playground/validator/v10"
)

// User contains user information
type User struct {
	FirstName      string     `validate:"required"`
	LastName       string     `validate:"required"`
	Age            uint8      `validate:"gte=0,lte=130"`
	Email          string     `validate:"required,email"`
	Gender         string     `validate:"oneof=male female prefer_not_to"`
	FavouriteColor string     `validate:"iscolor"`                // alias for 'hexcolor|rgb|rgba|hsl|hsla'
	Addresses      []*Address `validate:"required,dive,required"` // a person can have a home and cottage...
}

// Address houses a users address information
type Address struct {
	Street string `validate:"required"`
	City   string `validate:"required"`
	Planet string `validate:"required"`
	Phone  string `validate:"required"`
}

// use a single instance of Validate, it caches struct info
var validate *validator.Validate

func main() {

	validate = validator.New(validator.WithRequiredStructEnabled())

	validateStruct()
	validateVariable()
}

func validateStruct() {

	address := &Address{
		Street: "Eavesdown Docks",
		Planet: "Persphone",
		Phone:  "none",
	}

	user := &User{
		FirstName:      "Badger",
		LastName:       "Smith",
		Age:            135,
		Gender:         "male",
		Email:          "Badger.Smith@gmail.com",
		FavouriteColor: "#000-",
		Addresses:      []*Address{address},
	}

	// returns nil or ValidationErrors ( []FieldError )
	err := validate.Struct(user)
	if err != nil {

		// this check is only needed when your code could produce
		// an invalid value for validation such as interface with nil
		// value most including myself do not usually have code like this.
		if _, ok := err.(*validator.InvalidValidationError); ok {
			fmt.Println(err)
			return
		}

		for _, err := range err.(validator.ValidationErrors) {

			fmt.Println("*", err.Namespace())
			fmt.Println(err.Field())
			fmt.Println(err.StructNamespace())
			fmt.Println(err.StructField())
			fmt.Println(err.Tag())
			fmt.Println(err.ActualTag())
			fmt.Println(err.Kind())
			fmt.Println(err.Type())
			fmt.Println(err.Value())
			fmt.Println(err.Param())
			fmt.Println()
		}

		// from here you can create your own error messages in whatever language you wish
		return
	}

	// save user to database
}

func validateVariable() {

	myEmail := "joeybloggs.gmail.com"

	errs := validate.Var(myEmail, "required,email")

	if errs != nil {
		fmt.Println(errs) // output: Key: "" Error:Field validation for "" failed on the "email" tag
		return
	}

	// email ok, move on
}

```

上述的打印效果如下所示，也就是说validateStruct() 中遍历的每两行的打印效果是一样的（熟悉一下）。

```
* User.Age
Age
User.Age
Age
lte
lte
uint8
uint8
135
130

* User.FavouriteColor
FavouriteColor
User.FavouriteColor
FavouriteColor
iscolor
hexcolor|rgb|rgba|hsl|hsla
string
string
#000-


* User.Addresses[0].City
City
User.Addresses[0].City
City
required
required
string
string



Key: '' Error:Field validation for '' failed on the 'email' tag
```

#### 解析上述代码：

首先是定义了两个结构体，每个字段都有标签，重点是User内嵌套了Address。

```
// User contains user information
type User struct {
	FirstName      string     `validate:"required"`
	LastName       string     `validate:"required"`
	Age            uint8      `validate:"gte=0,lte=130"`
	Email          string     `validate:"required,email"`
	Gender         string     `validate:"oneof=male female prefer_not_to"`
	FavouriteColor string     `validate:"iscolor"`                // alias for 'hexcolor|rgb|rgba|hsl|hsla'
	Addresses      []*Address `validate:"required,dive,required"` // a person can have a home and cottage...
}

// Address houses a users address information
type Address struct {
	Street string `validate:"required"`
	City   string `validate:"required"`
	Planet string `validate:"required"`
	Phone  string `validate:"required"`
}
```

接着是 validateStruct() ，创建不符合字段要求的两个对象，`err := validate.Struct(user)`对user进行字段校验，显然是会出错的，进入到iferr之中，对err进行了两中类型断言，`*validator.InvalidValidationError`显然不对，要`validator.ValidationErrors`才对，进入到foreach循环中，进行了一系列的打印。从打印结果中来看，嵌套的结构体也被校验了，且遍历的每两行的打印效果是一样的（熟悉一下）。

```
func validateStruct() {

	address := &Address{
		Street: "Eavesdown Docks",
		Planet: "Persphone",
		Phone:  "none",
	}

	user := &User{
		FirstName:      "Badger",
		LastName:       "Smith",
		Age:            135,
		Gender:         "male",
		Email:          "Badger.Smith@gmail.com",
		FavouriteColor: "#000-",
		Addresses:      []*Address{address},
	}

	// returns nil or ValidationErrors ( []FieldError )
	err := validate.Struct(user)
	if err != nil {

		// this check is only needed when your code could produce
		// an invalid value for validation such as interface with nil
		// value most including myself do not usually have code like this.
		if _, ok := err.(*validator.InvalidValidationError); ok {
			fmt.Println(err)
			return
		}

		for _, err := range err.(validator.ValidationErrors) {

			fmt.Println("*", err.Namespace())
			fmt.Println(err.Field())
			fmt.Println(err.StructNamespace())
			fmt.Println(err.StructField())
			fmt.Println(err.Tag())
			fmt.Println(err.ActualTag())
			fmt.Println(err.Kind())
			fmt.Println(err.Type())
			fmt.Println(err.Value())
			fmt.Println(err.Param())
			fmt.Println()
		}

		// from here you can create your own error messages in whatever language you wish
		return
	}

	// save user to database
}
```

最后是`validateVariable()`，这个函数的关键一行在于`errs := validate.Var(myEmail, "required,email")`，这是对变量标明了校验的要求，即required非空和email邮箱格式。

```go
func validateVariable() {

	myEmail := "joeybloggs.gmail.com"

	errs := validate.Var(myEmail, "required,email")

	if errs != nil {
		fmt.Println(errs) // output: Key: "" Error:Field validation for "" failed on the "email" tag
		return
	}

	// email ok, move on
}
```

### 另外的例子

在实际编程中，发现别人在校验数据时是如下这样用的。先使用类型断言来判断err是不是validator.ValidationErrors这个类型的errors，如果不是那么ok为false，说明不是validator参数校验发生的错误，是前端请求参数错误的问题，返回请求参数错误给前端；如果ok为true，那么翻译validator.ValidationErrors，进行errs的翻译，然后传回前端。（Response开头的函数是封装返回信息的）

```go
//引用自博客项目的controller的user.go的注册服务
// 2.校验数据有效性
if err := c.ShouldBindJSON(&fo); err != nil {
	// 请求参数有误，直接返回响应
	zap.L().Error("SignUp with invalid param", zap.Error(err))
	// 判断err是不是 validator.ValidationErrors类型的errors
	errs, ok := err.(validator.ValidationErrors)
	if !ok {
		// 非validator.ValidationErrors类型错误直接返回
		ResponseError(c, CodeInvalidParams) // 请求参数错误，封装并返回
		return
	}
	// validator.ValidationErrors类型错误则进行翻译
	ResponseErrorWithMsg(c, CodeInvalidParams, removeTopStruct(errs.Translate(trans)))//封装并返回
	return // 翻译错误
}
```

## 自定义验证

### 0.总结：

1. 自定义字段验证注册自定义函数用`validator.RegisterValidation`

2. 结构体级别的验证（复合校验）自定义函数用 `validator.RegisterStructValidation`

3. 定制获取结构体字段的标签用`RegisterTagNameFunc` 

4. 定义翻译器比较复杂，直接看自定义翻译器的流程

   

### **1.自定义验证函数**

- ##### 自定义字段验证

  通过`validator.RegisterValidation` 方法可以注册一个自定义验证函数

  ```go
  // 定义一个自定义的验证器函数
  func notBlank(fl validator.FieldLevel) bool {
  	// 检查字段是否是字符串，并且非空
  	return fl.Field().String() != ""
  }
  
  func main(){
  	...
  	// 注册自定义的验证器
  	validate.RegisterValidation("notblank", notBlank)
  	...
  }
  ```

- ##### 自定义结构体级别验证

  结构体级别的验证允许你在整个结构体的上下文中执行验证逻辑。通过 `validator.RegisterStructValidation` 来实现

  ```go
  type User struct {
  	Password        string `validate:"required"`
  	ConfirmPassword string `validate:"required"`
  }
  
  // 自定义结构体级别的验证
  func userStructLevelValidation(sl validator.StructLevel) {
  	user := sl.Current().Interface().(User)
  
  	if user.Password != user.ConfirmPassword {
  		sl.ReportError(user.ConfirmPassword, "confirm_password", "ConfirmPassword", "eqfield", "password")
  	}
  }
  
  func main() {
  	...
  	// 注册结构体级别的验证器
  	validate.RegisterStructValidation(userStructLevelValidation, User{})
  	...
  }
  ```

### 2.自定义错误消息

当发现匹配错误的时候，遍历err，针对不同的tag返回不同的错误信息

```go
// 处理验证错误并自定义错误消息
	if err != nil {
		if errs, ok := err.(validator.ValidationErrors); ok {
			for _, e := range errs {
				switch e.Tag() {
				case "required":
					fmt.Printf("字段 %s 是必填的\n", e.Field())
				case "min":
					fmt.Printf("字段 %s 的值必须大于或等于 %s\n", e.Field(), e.Param())
				}
			}
		}
	}
```

### 3.自定义结构体标签处理

通过 `RegisterTagNameFunc` 可以定制如何获取结构体字段的标签。以下是一个例子：

```go
// 注册一个获取json tag的自定义方法
v.RegisterTagNameFunc(func(fld reflect.StructField) string {
    name := strings.SplitN(fld.Tag.Get("json"), ",", 2)[0]
    if name == "-" {
       return ""
    }
    return name
})
```

这段代码的作用是**自定义获取结构体字段的 `json` 标签名称**，以便在后续的表单验证或错误提示中使用该标签名，而不是结构体字段名。这在处理复杂的 JSON 序列化和反序列化时非常有用，尤其是在返回表单验证错误信息时可以使用前端熟悉的字段名称。

- #### 具体解析

1. **`v.RegisterTagNameFunc`**：这是 Go 的 `validator` 库提供的一个方法，用于注册一个函数，该函数用来获取结构体字段的标签名（即 `tag`）。你可以通过它来自定义获取标签名的逻辑。在这个例子中，函数会获取 `json` 标签。
   
2. **`fld reflect.StructField`**：传入的 `fld` 是 `reflect.StructField` 类型的参数，它代表结构体中的某个字段。通过它可以获取字段的所有信息，包括标签（`tag`）。

3. **`fld.Tag.Get("json")`**：这部分代码用于获取该字段的 `json` 标签。如果结构体字段上有 `json` 标签，例如：
   ```go
   type User struct {
       Name string `json:"name"`
       Age  int    `json:"age"`
   }
   ```
   它将会提取到 `json:"name"` 中的 `"name"` 作为字段名。

4. **`strings.SplitN(fld.Tag.Get("json"), ",", 2)[0]`**：这个代码片段会将 `json` 标签以逗号 `,` 为分隔符拆分成最多两部分，并返回第一部分。这是因为在 `json` 标签中，可能有其他选项，比如：
   ```go
   Name string `json:"name,omitempty"`
   ```
   在这种情况下，`strings.SplitN` 将会返回 `"name"`，忽略掉 `omitempty`。

5. **处理 `"-"` 标签**：
   ```go
   if name == "-" {
       return ""
   }
   ```
   如果 `json` 标签的内容是 `"-"`，这表示该字段不应该被序列化或反序列化（忽略该字段）。例如：
   ```go
   Name string `json:"-"`
   ```
   在这种情况下，函数会返回空字符串 `""`，表示跳过该字段。

6. **返回字段名**：
   ```go
   return name
   ```
   最后，返回字段的 `json` 标签名（如果没有 `json` 标签，则默认返回空字符串或字段名）。

- #### 作用场景


1. **校验时使用 `json` 名称**：当执行字段校验时，`validator` 库默认会使用 Go 语言中的结构体字段名。如果你想在错误信息中显示 `json` 标签名（前端熟悉的字段名），而不是 Go 代码中的结构体字段名，那么这段代码可以实现这样的需求。

   **示例**：如果字段 `User.Name` 触发了验证错误，你希望错误信息中显示的是 `name`（`json` 标签名），而不是 `Name`（Go 字段名），这段代码会帮助你实现这一点。

2. **方便前后端一致性**：前端通常使用 `json` 标签名发送请求或接收响应数据，而后端代码中的结构体字段名可能与 `json` 标签名不同。通过这个自定义函数，后端可以根据 `json` 标签名生成更加友好的错误信息，保持与前端一致的字段名，方便调试。

- #### 总结

这段代码的主要作用是：**在字段校验时，通过获取字段的 `json` 标签名，替代 Go 语言中的字段名**，从而确保校验错误信息中的字段名与前端传递的字段名保持一致。这让错误提示更加直观，也便于前后端协作。

### 4.自定义翻译器

翻译器的作用是为了使得增强错误信息的可读性。例如原始的错误信息可能长这样`Key: 'User.username' Error:Field validation for 'username' failed on the 'required' tag`，但是翻译器翻译过后为`username为必填字段`。为验证错误消息进行多语言支持，使用 `universal-translator` 包来实现。

使用流程如下：

1. 首先要new语言翻译器

   ```
   // 创建中文翻译器
   zhLocale := zh.New()
   uni := ut.New(zhLocale, zhLocale)
   trans, _ := uni.GetTranslator("zh")
   ```

2. 然后注册翻译器

   ```
   // 注册翻译器
   zh_translations.RegisterDefaultTranslations(validate, trans)
   ```

3. 最后在错误处理时，打印使用方法`Translate(trans)`就能实现翻译了

   ```
   e.Translate(trans)
   ```

完整的例子如下，可直接运行。其中`validate.RegisterTagNameFunc`注册了错误信息处理时获取tag中json标签后的名称，可以更好地明确错误信息。

```go
package main

import (
	"fmt"
	"reflect"

	"github.com/go-playground/locales/zh"
	ut "github.com/go-playground/universal-translator"
	"github.com/go-playground/validator/v10"
	zh_translations "github.com/go-playground/validator/v10/translations/zh"
)

type User struct {
	Username string `json:"username" validate:"required"`
	Age      int    `json:"age" validate:"gte=18,lte=60"`
}

func main() {
	// 创建验证器实例
	validate := validator.New()

	// 创建中文翻译器
	zhLocale := zh.New()
	uni := ut.New(zhLocale, zhLocale)// 第一个参数是备用（fallback）的语言环境，后面的参数是应支持的语言环境（支持多个）
	trans, _ := uni.GetTranslator("zh")

	// 注册翻译器
	zh_translations.RegisterDefaultTranslations(validate, trans)

	// 注册结构体字段名称的翻译（非必要）
	validate.RegisterTagNameFunc(func(fld reflect.StructField) string {
		return fld.Tag.Get("json")
	})

	// 示例数据
	user := User{
		Username: "",
		Age:      17,
	}

	// 执行验证
	err := validate.Struct(user)
	if err != nil {
		// 将验证错误翻译为中文
		errs := err.(validator.ValidationErrors)
		for _, e := range errs {
			fmt.Println(e.Translate(trans))
		}
		return
	}

	fmt.Println("验证通过！")
}
```

上述例子的打印结果如下：

```
username为必填字段
age必须大于或等于18
```

