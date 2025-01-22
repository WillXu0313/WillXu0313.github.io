---
title: geeRPC学习
date: 2025-01-22 11:25:00
categories:
- geektutu
---
# RPC

针对geeRPC进行了学习，原文链接：[geeRPC](https://geektutu.com/post/geerpc.html)

## 服务端与消息编码

以下是对`Codec`接口的详细解释：

### 1. 整体作用
`Codec`接口用于定义编解码器的通用行为。它抽象了编解码过程中涉及的关键操作，使得不同的编解码器实现可以遵循相同的接口规范，方便在程序中进行统一管理和替换。这种设计模式提高了代码的可维护性和可扩展性，特别是在需要处理多种编码格式的应用场景中。

### 2. 接口方法解释

- **`io.Closer`**
    - **含义**：这表明实现`Codec`接口的类型必须同时实现`io.Closer`接口的`Close()`方法。
    - **功能**：`Close()`方法主要用于释放编解码器在运行过程中占用的资源。例如，如果编解码器在处理过程中打开了文件、网络连接或者使用了一些缓存资源，当不再需要编解码器时，应该通过`Close()`方法来正确关闭和释放这些资源，以防止资源泄漏。

- **`ReadHeader(*Header) error`**
    - **含义**：此方法用于从输入源（如网络连接、文件等）读取消息头信息，并将其解析到`*Header`类型的对象中。
    - **参数**：接受一个指向`Header`结构体的指针作为参数。这个`Header`结构体包含了与消息相关的元信息，如`ServiceMethod`（服务方法标识）、`Seq`（序列号）和`Error`（错误信息）等。
    - **返回值**：如果在读取或解析消息头的过程中出现错误，该方法将返回一个非`nil`的`error`值。正常读取和解析完成后，`Header`结构体中的成员变量将被正确填充。

- **`ReadBody(interface{}) error`**
    - **含义**：用于从输入源读取消息体内容。
    - **参数**：接受一个`interface{}`类型的参数。这是一种灵活的设计，因为不同类型的消息体内容可以被传入，具体的编解码器实现需要根据编码格式将读取到的字节流转换为合适类型的数据，并存储到传入的`interface{}`对象所指向的内存空间中。
    - **返回值**：在读取消息体过程中，如果遇到错误，例如字节流格式不正确、读取到不完整的数据等，会返回相应的`error`值。

- **`Write(*Header, interface{}) error`**
    - **含义**：负责将消息头和消息体写入到输出目标（如网络连接、文件等）。
    - **参数**：接受两个参数，一个是指向`Header`结构体的指针，包含了要写入的消息头信息；另一个是`interface{}`类型，表示要写入的消息体内容。编解码器实现需要根据特定的编码格式将消息头和消息体转换为字节流后写入输出目标。
    - **返回值**：如果在写入过程中出现问题，比如网络连接中断、磁盘空间不足等，该方法会返回一个非`nil`的`error`值。

```go
type NewCodecFunc func(io.ReadWriteCloser) Codec

type Type string

const (
	GobType  Type = "application/gob"
	JsonType Type = "application/json" // not implemented
)

var NewCodecFuncMap map[Type]NewCodecFunc

func init() {
	NewCodecFuncMap = make(map[Type]NewCodecFunc)
	NewCodecFuncMap[GobType] = NewGobCodec
}
```

以下是对这段代码的详细解释：

### 1. `NewCodecFunc`类型定义
- **`type NewCodecFunc func(io.ReadWriteCloser) Codec`**
    - 这是一个函数类型的定义。`NewCodecFunc`类型的函数接受一个`io.ReadWriteCloser`类型的参数，`io.ReadWriteCloser`接口表示一个既可以读取、又可以写入并且可以关闭的对象（例如网络连接、文件等）。
    - 函数的返回值是一个实现了`Codec`接口的对象。这意味着`NewCodecFunc`类型的函数是用于创建特定编解码器实例的工厂函数。给定一个合适的`io.ReadWriteCloser`对象，它能创建出一个可以处理该输入输出源编解码的`Codec`实例。

### 2. `Type`类型和相关常量
- **`type Type string`**
    - 定义了一个新的类型`Type`，它是`string`类型的别名。这个类型用于表示编解码器的类型。
- **`const (GobType Type = "application/gob" JsonType Type = "application/json" // not implemented)`**
    - 这里定义了两个`Type`类型的常量。`GobType`被赋值为`"application/gob"`，代表`gob`编码类型；`JsonType`被赋值为`"application/json"`，代表`json`编码类型，不过这里有注释表明`json`类型的编解码器尚未实现。这些常量用于在程序中标识不同的编解码器类型。

### 3. `NewCodecFuncMap`变量和`init`函数
- **`var NewCodecFuncMap map[Type]NewCodecFunc`**
    - 声明了一个名为`NewCodecFuncMap`的变量，它是一个映射（`map`）类型。这个映射的键是`Type`类型（即编解码器类型），值是`NewCodecFunc`类型（即创建编解码器的函数）。这个映射用于存储不同类型编解码器的创建函数，通过编解码器类型作为键来获取相应的创建函数。
- **`func init() {... }`**
    - `init`函数是Go语言中的特殊函数，在包被初始化时自动执行。在这个`init`函数中：
        - **创建映射**：`NewCodecFuncMap = make(map[Type]NewCodecFunc)`语句创建了`NewCodecFuncMap`映射。
        - **初始化映射元素**：`NewCodecFuncMap[GobType] = NewGobCodec`将`GobType`（`"application/gob"`）这个编解码器类型与`NewGobCodec`函数关联起来。这里假设`NewGobCodec`是一个已经定义好的`NewCodecFunc`类型的函数，用于创建`gob`编码的编解码器。这使得程序在需要创建`gob`编解码器时，可以通过`NewCodecFuncMap[GobType]`来获取创建函数。这种设计方便了根据不同的编解码器类型来动态创建相应的编解码器实例。

## 高性能客户端

总的来讲，客户端需要实现的功能主要包括如下几点：

1. 创建连接
2. 接收响应
3. 发送请求

### 数据结构设计

#### call

在RPC中，一次调用（call）所调用的方法具有特定的格式要求。

```
func (t *T) MethodName(argType T1, replyType *T2) error
```

具体表现为：exported和type，函数和形参都要是导出的（首字母大写），响应体要是指针（为了写响应），返回必须是错误类型

- the method’s type is exported.
- the method is exported.
- the method has two arguments, both exported (or builtin) types.
- the method’s second argument is a pointer.
- the method has return type error.

因此针对上述call的调用，对Call结构体，一定需要的参数有ServiceMethod、Args、Reply、Error。除此之外有标识call序号的seq和用于传递完成信号的通道Done，Done主要是为了方便异步调用结束RPC调用。注意参数都要开头大写表示导出，这样其他包才能访问。

实现done方法用于将call、放入到Done通道中。

```
// Call represents an active RPC.
type Call struct {
	Seq           uint64
	ServiceMethod string      // format "<service>.<method>"
	Args          interface{} // arguments to the function
	Reply         interface{} // reply from the function
	Error         error       // if error occurs, it will be set
	Done          chan *Call  // Strobes when call is complete.
}

func (call *Call) done() {
	call.Done <- call
```

#### client

Client的字段很多：

- cc是编解码器
- opt是可选项，可选择编解码方式
- sending是互斥锁，控制请求发送过程的有序
- header是请求头，每个客户端维护一个请求头，在call中复用
- sqe是发送的请求编号
- pending存储未处理完的请求，键是编号，值是 Call 实例。
- closing 和 shutdown 任意一个值置为 true，则表示 Client 处于不可用的状态，但有些许的差别，closing 是用户主动关闭的，即调用 `Close` 方法，而 shutdown 置为 true 一般是有错误发生。

```go
// Client represents an RPC Client.
// There may be multiple outstanding Calls associated
// with a single Client, and a Client may be used by
// multiple goroutines simultaneously.
type Client struct {
	cc       codec.Codec//编解码器
	opt      *Option//可选项，选择编码方式
	sending  sync.Mutex // protect following
	header   codec.Header
	mu       sync.Mutex // protect following
	seq      uint64
	pending  map[uint64]*Call//未处理完的请求
	closing  bool // user has called Close
	shutdown bool // server has told us to stop
}
```

基本的关闭和检查可用，`var _ io.Closer = (*Client)(nil)`检查实现io.Closer的接口方法

```
var _ io.Closer = (*Client)(nil)

var ErrShutdown = errors.New("connection is shut down")

// Close the connection
func (client *Client) Close() error {
	client.mu.Lock()
	defer client.mu.Unlock()
	if client.closing {
		return ErrShutdown
	}
	client.closing = true
	return client.cc.Close()
}

// IsAvailable return true if the client does work
func (client *Client) IsAvailable() bool {
	client.mu.Lock()
	defer client.mu.Unlock()
	return !client.shutdown && !client.closing
}
```

### Call调用方法

- registerCall：将参数 call 添加到 client.pending 中，并更新 client.seq。
- removeCall：根据 seq，从 client.pending 中移除对应的 call，并返回。
- terminateCalls：服务端或客户端发生错误时调用，将 shutdown 设置为 true，且将错误信息通知所有 pending 状态的 call。

#### 注册Call调用

注册一个Call到Client，放入该Client的处理序列中

```go
func (client *Client) registerCall(call *Call) (uint64, error) {
	client.mu.Lock()
	defer client.mu.Unlock()
	if client.closing || client.shutdown {
		return 0, ErrShutdown
	}
	call.Seq = client.seq
	client.pending[call.Seq] = call
	client.seq++
	return call.Seq, nil
}
```

#### 移除Call

将某个特定的Call从待完成序列中移除。

- 在receive中调用removeCall获取到待处理的某个call，处理服务端发送的响应。

- 在send中调用removeCall用于处理编解码发送请求时发生的错误，将错误的call移除并处理错误。

```go
func (client *Client) removeCall(seq uint64) *Call {
	client.mu.Lock()
	defer client.mu.Unlock()
	call := client.pending[seq]
	delete(client.pending, seq)
	return call
}
```

#### 中止Call

中止出现错误的调用，将错误信息通知所有 pending 状态的 call。该方法标记了客户端shutdown错误，这个客户端都不能用了，且所有未完成的call都被标记了错误。因此只有发生致命错误才调用，也就只有在rceive的末尾看到。

```go
func (client *Client) terminateCalls(err error) {
	client.sending.Lock()
	defer client.sending.Unlock()
	client.mu.Lock()
	defer client.mu.Unlock()
	client.shutdown = true
	for _, call := range client.pending {
		call.Error = err
		call.done()
	}
}
```

### Client调用方法

#### 接收响应

接收到的响应有三种情况：

- call 不存在，可能是请求没有发送完整，或者因为其他原因被取消，但是服务端仍旧处理了。
- call 存在，但服务端处理出错，即 h.Error 不为空。
- call 存在，服务端处理正常，那么需要从 body 中读取 Reply 的值。

因此这决定了receive方法的具体逻辑。它处于一个循环状态不断接收请求，直到发生错误退出。在一次循环中，它先获取请求头，然后根据请求头中包含的序列号seq取出一个call，对这个call依次执行上述三种响应的处理情况。

在for循环外有terminateCalls，只要发生错误就中止所有请求。这里的错误有服务端的不正确处理（前两错误个分支）和网络问题导致的短暂读写错误（`err = client.cc.ReadBody(call.Reply)`），不过`terminateCalls` 的使用简化处理逻辑，优先保证稳定性，所以没有考虑短暂的网络中断然后恢复。在更复杂的实现中，可以用重试机制、连接状态检查或重新连接等方式来处理临时错误，而不是直接关闭客户端。

要确保读取的完整性，即`ReadHeader`和`ReadBody`都要调用读取，哪怕没有读取Body到具体变量中存储。因此前两个出错分支上有`client.cc.ReadBody(nil)`。

```go
func (client *Client) receive() {
	var err error
	for err == nil {
		var h codec.Header
		if err = client.cc.ReadHeader(&h); err != nil {
			break
		}
		call := client.removeCall(h.Seq)
		switch {
		case call == nil:
			// it usually means that Write partially failed
			// and call was already removed.
			err = client.cc.ReadBody(nil)
		case h.Error != "":
			call.Error = fmt.Errorf(h.Error)
			err = client.cc.ReadBody(nil)
			call.done()
		default:
			err = client.cc.ReadBody(call.Reply)
			if err != nil {
				call.Error = errors.New("reading body " + err.Error())
			}
			call.done()
		}
	}
	// error occurs, so terminateCalls pending calls
	client.terminateCalls(err)
}
```

#### 创建实例

创建Client实例，首先需要完成协议交换，即发送 `Option` 信息给服务端。协商好消息的编解码方式之后，再创建一个子协程调用 `receive()` 接收响应。

NewClient方法接受两个参数，一个网络连接和一个可选项。首先根据Option获得编解码方式的构造函数，然后发送Option到服务端，最后调用newClientCodec方法真正创建Client实例。

newClientCodec方法接受编解码器和可选项两个参数。它真正创建Client实例，同时开启receive协程用于接收信息，返回创建好的Client实例。

```go
func NewClient(conn net.Conn, opt *Option) (*Client, error) {
	f := codec.NewCodecFuncMap[opt.CodecType]
	if f == nil {
		err := fmt.Errorf("invalid codec type %s", opt.CodecType)
		log.Println("rpc client: codec error:", err)
		return nil, err
	}
	// send options with server
	if err := json.NewEncoder(conn).Encode(opt); err != nil {
		log.Println("rpc client: options error: ", err)
		_ = conn.Close()
		return nil, err
	}
	return newClientCodec(f(conn), opt), nil
}

func newClientCodec(cc codec.Codec, opt *Option) *Client {
	client := &Client{
		seq:     1, // seq starts with 1, 0 means invalid call
		cc:      cc,
		opt:     opt,
		pending: make(map[uint64]*Call),
	}
	go client.receive()
	return client
}
```

#### 创建连接

实现 `Dial` 函数，便于用户传入服务端地址，创建 Client 实例。为了简化用户调用，通过 `...*Option` 将 Option 实现为可选参数。

parseOptions解析opts，填充option。option是可选的选项，有默认选择。

Dial是用户传入服务端地址，创建 Client 实例的接口。

```
func parseOptions(opts ...*Option) (*Option, error) {
	// if opts is nil or pass nil as parameter
	if len(opts) == 0 || opts[0] == nil {
		return DefaultOption, nil
	}
	if len(opts) != 1 {
		return nil, errors.New("number of options is more than 1")
	}
	opt := opts[0]
	opt.MagicNumber = DefaultOption.MagicNumber
	if opt.CodecType == "" {
		opt.CodecType = DefaultOption.CodecType
	}
	return opt, nil
}

// Dial connects to an RPC server at the specified network address
func Dial(network, address string, opts ...*Option) (client *Client, err error) {
	opt, err := parseOptions(opts...)
	if err != nil {
		return nil, err
	}
	conn, err := net.Dial(network, address)
	if err != nil {
		return nil, err
	}
	// close the connection if client is nil
	defer func() {
		if client == nil {
			_ = conn.Close()
		}
	}()
	return NewClient(conn, opt)
}
```

#### 发送请求

获取锁->注册call->准备header->编码并发送请求

```go
func (client *Client) send(call *Call) {
	// make sure that the client will send a complete request
	client.sending.Lock()
	defer client.sending.Unlock()

	// registry this call.
	seq, err := client.registerCall(call)
	if err != nil {
		call.Error = err
		call.done()
		return
	}

	// prepare request header
	client.header.ServiceMethod = call.ServiceMethod
	client.header.Seq = seq
	client.header.Error = ""

	// encode and send the request
	if err := client.cc.Write(&client.header, call.Args); err != nil {
		call := client.removeCall(seq)
		// call may be nil, it usually means that Write partially failed,
		// client has received the response and handled
		if call != nil {
			call.Error = err
			call.done()
		}
	}
}
```



#### 接口调用

- `Go` 和 `Call` 是客户端暴露给用户的两个 RPC 服务调用接口，`Go` 是一个异步接口，返回 call 实例。
- `Call` 是对 `Go` 的封装，阻塞 call.Done，等待响应返回，是一个同步接口。

```
// Go invokes the function asynchronously.
// It returns the Call structure representing the invocation.
func (client *Client) Go(serviceMethod string, args, reply interface{}, done chan *Call) *Call {
	if done == nil {
		done = make(chan *Call, 10)
	} else if cap(done) == 0 {
		log.Panic("rpc client: done channel is unbuffered")
	}
	call := &Call{
		ServiceMethod: serviceMethod,
		Args:          args,
		Reply:         reply,
		Done:          done,
	}
	client.send(call)
	return call
}

// Call invokes the named function, waits for it to complete,
// and returns its error status.
func (client *Client) Call(serviceMethod string, args, reply interface{}) error {
	call := <-client.Go(serviceMethod, args, reply, make(chan *Call, 1)).Done
	return call.Error
}
```

#### others

call结束了都会被放入自己的done用于传递结束信息

## 服务注册

RPC框架的一个基础能力是：像调用本地程序一样调用远程服务。那如何将程序映射为服务呢？那么对 Go 来说，这个问题就变成了如何将结构体的方法映射为服务。为了动态地加载方法，我们需要使用反射。

通过反射，我们能够非常容易地获取某个结构体的所有方法，并且能够通过方法，获取到该方法所有的参数类型与返回值。

首先通过反射实现结构体与服务的映射关系，代码独立放置在 `service.go` 中。

然后将`service.go`中实现的结构体与服务的映射关系功能集成到`Server`中，使得`Server`拥有调用具体服务的功能。

### 熟悉反射

[Go反射终极指南：从基础到高级全方位解析 - 个人文章 - SegmentFault 思否](https://segmentfault.com/a/1190000044313900)

以下是个demo

```
func main() {
	var wg sync.WaitGroup  // 创建一个 sync.WaitGroup 实例
	typ := reflect.TypeOf(&wg)  // 获取 sync.WaitGroup 的反射类型，注意这里传递的是指针类型
	for i := 0; i < typ.NumMethod(); i++ {  // 遍历类型的所有方法
		method := typ.Method(i)  // 获取第 i 个方法
		argv := make([]string, 0, method.Type.NumIn())  // 存储方法的入参类型
		returns := make([]string, 0, method.Type.NumOut())  // 存储方法的返回值类型

		// 获取方法的入参类型，从第 1 个开始，因为第 0 个是接收者（wg）
		for j := 1; j < method.Type.NumIn(); j++ {
			argv = append(argv, method.Type.In(j).Name())  // 将入参类型名称添加到 argv
		}

		// 获取方法的返回值类型
		for j := 0; j < method.Type.NumOut(); j++ {
			returns = append(returns, method.Type.Out(j).Name())  // 将返回类型名称添加到 returns
		}

		// 打印方法签名：方法名、入参类型、返回类型
		log.Printf("func (w *%s) %s(%s) %s",
			typ.Elem().Name(),  // 获取类型的元素名称（不含指针）
			method.Name,  // 方法名
			strings.Join(argv, ","),  // 入参类型
			strings.Join(returns, ","))  // 返回值类型
	}
}
```

reflect.Type类型的变量通过Elem()获取具体类型， It panics if the type's Kind is not Array, Chan, Map, Pointer, or Slice.

`Elem`方法主要用于获取指针、接口等类型所指向或包含的底层类型信息，反正就是获取具体底层信息。

func (Type) Method(int) Method
Method returns the i'th method in the type's method set. It panics if i is not in the range [0, NumMethod()).


1. 方法获取
reflect.Type类型提供了方法来获取类型中定义的方法相关内容。可以使用NumMethod()方法来获取类型中定义的方法数量，它返回一个int值，表示该类型所包含的方法个数。
2. 单个方法信息
对于每个方法，可以通过索引（从 0 到NumMethod() - 1）使用Method(int)方法来获取关于特定方法的详细信息。这个方法返回一个reflect.Method类型的值，reflect.Method结构体包含了以下信息：
Name：方法的名称，是一个字符串。例如，对于结构体类型中的一个方法func (s MyStruct) MyMethod() {}，其名称就是"MyMethod"。
Type：方法的类型，是一个reflect.Type类型。这个类型信息包含了方法的签名，包括参数类型和返回值类型。例如，对于上述MyMethod方法，如果它接受一个int参数并返回一个string，那么Type信息将反映出这种参数和返回值的类型结构。可以进一步通过这个Type信息使用反射方法来分析方法的参数个数、类型以及返回值类型等细节。
Func：这是一个reflect.Value类型，表示方法的函数值。不过需要注意的是，这个函数值是一个未绑定的函数值，即它没有和特定的接收者绑定。在调用这个函数值时，需要提供接收者的值（在反射中通过合适的方式准备接收者和参数的值，然后使用Call方法调用）。
### Service

#### methodType

每一个 methodType 实例包含了一个方法的完整信息。包括：

- method：方法本身
- ArgType：第一个参数的类型
- ReplyType：第二个参数的类型
- numCalls：后续统计方法调用次数时会用到

```go
type methodType struct {
	method    reflect.Method
	ArgType   reflect.Type
	ReplyType reflect.Type
	numCalls  uint64
}
```

同时methodType实现了自身的三个方法：

- NumCalls：获取方法调用次数numCalls

- newArgv：生成方法的参数值 `argv`，依据 `m.ArgType` 创建相应的类型

  - 若 `ArgType` 是指针类型，则 `argv` 是 `m.ArgType` 元素类型的新指针。
  - 若 `ArgType` 是非指针类型，则直接创建 `ArgType` 的值。

- newReplyv：生成方法的返回值 `replyv`，确保其为指针类型。

  *若 `ReplyType` 为 `map` 或 `slice`，则将其初始化为空 `map` 或 `slice`，避免 `nil` 响应。如果是结构体类型，返回其全是字段零值的指针，其字段零值一般是有效的可用直接使用，但如果字段里面有切片或者map，切片或者map还是没有正确初始化，是nil，要小心。

New方法返回指针，因此在newArgv中对指针和值处理方式不同，确保返回值符合要求。

newArgv中`Kind()`方法用于获取参数的类型种类信息。

newPeplyv中`Elem()`方法用于获取指针所指向的元素类型。

```go
func (m *methodType) NumCalls() uint64 {
	return atomic.LoadUint64(&m.numCalls)
}

func (m *methodType) newArgv() reflect.Value {
	var argv reflect.Value
	// arg may be a pointer type, or a value type
	if m.ArgType.Kind() == reflect.Ptr {
		argv = reflect.New(m.ArgType.Elem())
	} else {
		argv = reflect.New(m.ArgType).Elem()
	}
	return argv
}

func (m *methodType) newReplyv() reflect.Value {
	// reply must be a pointer type
	replyv := reflect.New(m.ReplyType.Elem())
	switch m.ReplyType.Elem().Kind() {
	case reflect.Map:
		replyv.Elem().Set(reflect.MakeMap(m.ReplyType.Elem()))
	case reflect.Slice:
		replyv.Elem().Set(reflect.MakeSlice(m.ReplyType.Elem(), 0, 0))
	}
	return replyv
}
```

#### Service

一个service实例记录一个结构体实例的所有方法

- name：映射的结构体的名字
- typ：type，结构体类型
- rcvr：receiver，即结构体的实例本身，保留 rcvr 是因为在调用时需要 rcvr 作为第 0 个参数
- method 是 map 类型，存储映射的结构体的所有符合条件的方法

```
type service struct {
	name   string
	typ    reflect.Type
	rcvr   reflect.Value
	method map[string]*methodType
}
```

接下来，完成构造函数 `newService`，**入参**是任意需要映射为服务的**结构体实例**。

流程：通过反射填充service实例字段，通过name检查导出性，注册方法，返回service实例。

细节：

Indirect返回指针指向的值。Indirect returns the value that v points to. If v is a nil pointer, Indirect returns a zero Value. If v is not a pointer, Indirect returns v.

构造函数中关于反射的写法很规范，避免了很多问题。使用Indirect方法来解析，能确保获取到真正的方法的名字，哪怕rcvr接口实际上是个指针，都能通过转化获取到真实的结构体的名字。如果要直接从`rcvr`获取`name`（类型名称），需要看`rcvr`的具体类型是接口、指针、值来确定，那就相当麻烦。

type好像无所谓，获取到指针就指针类型了，反正也能反映结构体信息。

```
func newService(rcvr interface{}) *service {
	s := new(service)
	s.rcvr = reflect.ValueOf(rcvr)
	s.name = reflect.Indirect(s.rcvr).Type().Name()
	s.typ = reflect.TypeOf(rcvr)
	if !ast.IsExported(s.name) {
		log.Fatalf("rpc server: %s is not a valid service name", s.name)
	}
	s.registerMethods()
	return s
}

func (s *service) registerMethods() {
	s.method = make(map[string]*methodType)
	for i := 0; i < s.typ.NumMethod(); i++ {
		method := s.typ.Method(i)
		mType := method.Type
		if mType.NumIn() != 3 || mType.NumOut() != 1 {
			continue
		}
		if mType.Out(0) != reflect.TypeOf((*error)(nil)).Elem() {
			continue
		}
		argType, replyType := mType.In(1), mType.In(2)
		if !isExportedOrBuiltinType(argType) || !isExportedOrBuiltinType(replyType) {
			continue
		}
		s.method[method.Name] = &methodType{
			method:    method,
			ArgType:   argType,
			ReplyType: replyType,
		}
		log.Printf("rpc server: register %s.%s\n", s.name, method.Name)
	}
}

func isExportedOrBuiltinType(t reflect.Type) bool {
	return ast.IsExported(t.Name()) || t.PkgPath() == ""
}
```

`registerMethods` 过滤出了符合条件的方法：

- 两个导出或内置类型的入参（反射时为 3 个，第 0 个是自身，类似于 python 的 self，java 中的 this）
- 返回值有且只有 1 个，类型为 error

最后，我们还需要实现 `call` 方法，即能够通过反射值调用方法。

- 入参：一个方法信息的结构体m，请求参数和响应参数的反射值
- 返回值：error

- 具体流程：首先对numsCalls自增，然后通过`Func`获取可调用的函数值，再用Call调用函数返回调用的返回值，这是个error类型，检查错误并返回。

```
func (s *service) call(m *methodType, argv, replyv reflect.Value) error {
	atomic.AddUint64(&m.numCalls, 1)
	f := m.method.Func
	returnValues := f.Call([]reflect.Value{s.rcvr, argv, replyv})
	if errInter := returnValues[0].Interface(); errInter != nil {
		return errInter.(error)
	}
	return nil
}
```

### Server

1. Server集成注册服务功能，实现方法`Register`，方法`Register`调用`newService`注册一个结构体（服务就是结构体）
2. `findService`通过 `ServiceMethod` 从 `serviceMap` 中找到对应的 `service`。
3. Server实现对客户端调用的方法信息读取`ReadRequest`和实际处理`HandleRequest`

`findService` 的实现看似比较繁琐，但是逻辑还是非常清晰的。因为 ServiceMethod 的构成是 “Service.Method”，因此先将其分割成 2 部分，第一部分是 Service 的名称，第二部分即方法名。现在 serviceMap 中找到对应的 service 实例，再从 service 实例的 method 中，找到对应的 methodType。

## 超时处理

我理解的超时体现在三个方面：创建连接超时、客户端调用超时、服务端处理超时

具体来看整个远程调用过程，对客户端来说超时的地方为：

- 客户端和服务端建立连接超时（连接
- 客户端发送请求到服务端超时，即写报文超时（在写发
- 客户端等待服务端响应超时，服务端可能挂死了（在等
- 客户端处理服务端响应超时，即读报文超时（在读

对服务端来说超时的地方：

- 服务端读取客户端请求超时，即读报文超时（在读
- 服务端处理客户端请求超时（调用映射服务的方法超时），即处理超时（在处理
- 服务端响应客户端请求超时，即写报文超时（在写发

#### 创建连接超时

1.对超时设定的参数放在Option中，新增`ConnectTimeout`和`handleTimeout`两个参数，`ConnectTimeout`限制连接超时，`handleTimeout`控制服务端的处理超时。`ConnectTimeout` 默认值为 10s，`HandleTimeout` 默认值为 0，即不设限。

2.客户端创建连接超时，对`Dial`套娃调用`dialTimeout`，区别如下

1. 调用net.DialTimeout实现与服务端建立连接超时的处理
2. 使用子协程创建客户端实例（内含与服务端交换opt达成共识），通过通道返回创建好的客户端实例。这个创建过程带超时处理，若有设置连接超时，`dialTimeout`等待相应时间后返回错误结果；若没有设置连接超时，则等待子协程返回客户端实例，返回结果。具体实现上使用select-case语句，一个超时分支，一个正常结果分支。

#### 客户端Call调用超时

`Client.Call` 的超时处理机制，使用 context 包实现，控制权交给用户，控制更为灵活。用户使用`context.WithTimeout`创建具备超时检测能力的 context 对象来控制，使用如下：

```go
ctx, _ := context.WithTimeout(context.Background(), time.Second)
var reply int
err := client.Call(ctx, "Foo.Sum", &Args{1, 2}, &reply)
```

`Client.Call`方法使用`select+chan` ，由context上下文的Done分支实现超时响应，正常处理完call就从call.Done读取call，返回其错误。

#### 服务端处理超时

和客户端类似，使用 `time.After()` 结合 `select+chan` 实现超时机制。

整个过程拆分为 `called` 和 `sent` 两个阶段，即调用和发送。使用`send`和`call`两个通道来区分发送和调用，确保`sendResponse` 仅调用一次，即异常处理和正确调用中都只调用一次`sendResponse`。

流程1：在设置超时下，call调用超时，主线程select在<-time.After(timeout)分支触发超时，发送响应到客户端，结束主线程，called和sent全部阻塞，其信号不会由子协程通知到主线程。（子协程阻塞在call调用那一行，进一步使反射的Call上，是不是应该添加超时措施来限制子协程一直占用资源？**channel泄露问题**再增加主线程通知子协程关闭？可是阻塞在call上，进一步应该限制call调用时间？）

流程2：在设置超时下，call调用出错返回异常，将called信号发送到主线程，主线程select进入called分支，阻塞等待send信号。子协程进入错误处理，直接发送响应，将send信号发送到主线程，主线程接收信号结束。（sendResponse会不会超时->Write会不会超时？答案是不会！Write是enc将数据写到缓冲区就结束了，真正写数据在`Flush`调用时，而这个操作是在defer中被调用的）

流程3：call调用正常返回，子协程触发called信号和send信号，主线程接收信号并结束处理。





问题：Call调用卡在select上，是对call的返回处理不当，提前读取了Done

## 支持HTTP协议

之前都是通过TCP协议实现客户端和服务端之间的通信，比较局限，因此考虑兼容HTTP协议增加可用性。简化设计，仿照代理服务器，HTTP使用CONNECT请求向RPC服务端建立连接，利用HTTP的隧道机制转而建立RPC的连接，相当于绕了一下HTTP初步建立起连接，然后直接操纵TCP。（不过这种使用还是怪怪的，本质上客户端的连接还是粗放地使用TCP协议，只是包装成了发送CONECT请求的字符，只是利用了HTTP协议的连接协议阶段，后续调用还是使用RPC的Call和Go。

服务端的handle函数直接hijack允许直接操控tcp连接，后续是直接走tcp的。而handle函数终究是调用到了serveCodec来不断处理请求，ServerHTTP就没有结束。

![image-20241108154905695](C:/Users/%E8%AE%B8%E4%BC%9F%E5%BC%BA/AppData/Roaming/Typora/typora-user-images/image-20241108154905695.png)

好一个简陋的支持HTTP协议，只用一次HTTP，悄咪咪就把它换成TCP了，客户端后头还是用的tcp。

客户端本质上是用的TCP协议来传输，它发送一个CONNECT方法开头、带有服务端处理RPC的路径的字符流到服务端，服务端通过监听 TCP 请求端口，并在接收到 `CONNECT` 请求时，将请求转交给对应的 HTTP 处理逻辑。具体讲，服务端通过监听 TCP 请求端口，当客户端发送类似 `CONNECT /_geeprc_ HTTP/1.0` 请求时，服务端会将这个请求**视为 HTTP 请求**，并根据路径 `_geeprc_` 使用 HTTP 路由来处理。实际上，服务端利用 `http.ServeHTTP` 将请求转交给适当的处理函数，自动识别并响应这个请求。

服务端要实现的方法：

- ServeHTTP实现接口，一是RPC调用，一是Debug调用
- HandleHTTP外部调用此方法以启动路由，其调用`http.Handle`来注册defaultRPCPath到server

客户端要实现的方法：在TCP上套一层HTTP

- NewHTTPClient：通过HTTP协议向服务端发CONNECT请求建立连接，
- DialHTTP：通过HTTP协议建立连接，其调用dialTimeout，dialTimeout可支持不同的方式创建client，此处选择NewHTTPClient
- XDial：支持不同协议的连接

#### 服务端HTTP->RPC

在Go中处理 HTTP 请求需要调用HTTP包中的Handle方法来注册路由和处理函数

```
package http
// Handle registers the handler for the given pattern
// in the DefaultServeMux.
// The documentation for ServeMux explains how patterns are matched.
func Handle(pattern string, handler Handler) { DefaultServeMux.Handle(pattern, handler) }
```

而Handler是一个接口，只需要实现接口 Handler 即可作为一个 HTTP Handler 处理 HTTP 请求。而接口 Handler 只定义了一个方法 `ServeHTTP`，实现该方法即可。（隐式实现是有点恼火，一个结构体类型实现了该接口的所有方法，那么它就实现了这个接口）

```
type Handler interface {
    ServeHTTP(w ResponseWriter, r *Request)
}
```

因此对server这个结构体类型，实现ServeHTTP方法，就实现了Handler接口，之后调用`http.Handle`来注册即可。

#### 服务端Debug

**模板文件**

1. **模板文本内容（`debugText`）**

整体结构

这是一个HTML模板，用于生成包含特定Go RPC服务调试信息的HTML页面。

`<html>`、`<body>`和`<title>`标签

```html
<html>
	<body>
	<title>GeeRPC Services</title>
```
这是HTML文档的基本结构部分，定义了文档类型为HTML，包含一个`body`标签用于页面内容展示，以及一个`title`标签，标题为`GeeRPC Services`，表明这个页面是与GeeRPC服务相关的调试信息页面。

模板动作（`{{range...}}`）

```html
{{range.}}
```
这里使用了Go模板语言中的`range`动作。在这个模板上下文中，`.`代表传递给模板的数据。这里的`range`表示对传递进来的数据进行迭代。从后续的代码可以推断，传递给模板的数据应该是一个切片或者数组类型，每个元素都包含了服务相关的信息（包括服务名和方法信息等）。

服务信息展示部分

```html
	<hr>
	Service {{.Name}}
	<hr>
```
在每次迭代中（针对每个服务），先绘制一条水平分隔线（`<hr>`），然后展示服务的名称（`{{.Name}}`），这里的`Name`是数据结构中的一个字段（从后面完整的模板代码可以推断出），通过模板语法将服务名称嵌入到HTML中，再绘制一条水平分隔线。

方法信息表格部分

```html
		<table>
		<th align=center>Method</th><th align=center>Calls</th>
```
创建一个HTML表格，用于展示方法相关信息。表格有表头（`<th>`），两列分别是`Method`（方法）和`Calls`（调用次数），表头内容居中显示。

内层`range`动作（方法遍历）

```html
		{{range $name, $mtype :=.Method}}
```
这是一个内层的`range`动作，用于遍历当前服务的方法信息。这里使用了两个变量`$name`和`$mtype`，从当前服务元素中的`Method`字段（从后面代码可以推断这是一个`map`类型，键为方法名，值为包含方法类型信息的结构体）获取数据。`$name`用于存储方法名，`$mtype`用于存储方法相关的类型信息结构体。

表格行数据填充

```html
			<tr>
			<td align=left font=fixed>{{$name}}({{$mtype.ArgType}}, {{$mtype.ReplyType}}) error</td>
			<td align=center>{{$mtype.NumCalls}}</td>
			</tr>
```
对于每个方法，创建一个表格行（`<tr>`）。在第一列（`<td>`）中，展示方法名（`$name`）以及方法的参数类型（`$mtype.ArgType`）和返回值类型（`$mtype.ReplyType`），格式为`方法名(参数类型, 返回值类型) error`，文本左对齐，使用固定宽度字体。在第二列中，展示方法的调用次数（`$mtype.NumCalls`），内容居中显示。

2. **模板创建与解析（`template.Must(template.New("RPC debug").Parse(debugText))`）**

`template.New("RPC debug")`

创建一个新的模板实例，名称为`"RPC debug"`。这个名称可以用于后续的模板操作，比如在模板缓存或者错误处理中识别特定的模板。

`.Parse(debugText)`

调用新创建模板实例的`Parse`方法，将`debugText`（前面定义的HTML模板字符串）解析为模板内部的数据结构。这个过程会检查模板语法是否正确，如果有错误会返回一个非`nil`的错误值。

`template.Must`

`template.Must`是一个辅助函数，它接受一个模板实例和一个可能的错误值（这里是`template.New("RPC debug").Parse(debugText)`的结果）。如果错误值为`nil`，则返回模板实例；如果错误值不为`nil`，则`Must`函数会触发`panic`，使程序异常终止。这样可以确保在模板解析出现问题时能及时发现并停止程序，避免在运行时使用错误的模板。

总的来说，这段代码定义了一个HTML模板用于展示RPC服务的调试信息，包括服务名称和每个服务下的方法名称、参数类型、返回值类型以及方法的调用次数，并且通过`template`包的相关函数创建和解析了这个模板，确保模板的正确性。

**数据处理和渲染**

使用`server.serviceMap.Range(func(namei, svci interface{}) bool {...}`将map中地数据读取到切片`services`中，再使用`debug.Execute(w, services)`将services切片传递到模板文本debug并渲染到w上。

```
type debugHTTP struct {
	*Server
}

type debugService struct {
	Name   string
	Method map[string]*methodType
}

// Runs at /debug/geerpc
func (server debugHTTP) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	// Build a sorted version of the data.
	var services []debugService
	server.serviceMap.Range(func(namei, svci interface{}) bool {
		svc := svci.(*service)
		services = append(services, debugService{
			Name:   namei.(string),
			Method: svc.method,
		})
		return true
	})
	err := debug.Execute(w, services)
	if err != nil {
		_, _ = fmt.Fprintln(w, "rpc: error executing template:", err.Error())
	}
}
```

#### 客户端

向tcp建立的连接写入CONNECT请求的字符流

```
_, _ = io.WriteString(conn, fmt.Sprintf("CONNECT %s HTTP/1.0\n\n", defaultRPCPath))
```

尝试从conn连接中读取响应，`bufio.NewReader(conn)`创建读取器，`&http.Request{Method: "CONNECT"})`提供解读响应的上下文，提供解读应该采用CONNECT方法。

```
resp, err := http.ReadResponse(bufio.NewReader(conn), &http.Request{Method: "CONNECT"})
```

详细：

bufio.NewReader(conn)
创建读取器：bufio.NewReader函数接受一个io.Reader类型的参数（这里是conn，通常是一个网络连接对象，实现了io.Reader接口），并创建一个带缓冲的读取器。缓冲读取器可以更高效地读取数据，它会在内部缓冲区中预读一部分数据，减少频繁的底层I/O操作。这在处理网络数据时特别有用，因为网络I/O通常相对较慢。
&http.Request{Method: "CONNECT"}
创建HTTP请求对象（部分初始化）：这里创建了一个http.Request结构体的实例，并只初始化了Method字段为"CONNECT"。http.Request结构体用于表示一个HTTP请求，通常包含更多的字段，如URL、Header、Body等，但在这种情况下，只需要指定请求方法。CONNECT请求方法用于指示客户端希望建立一个到指定服务器和端口的隧道连接。
http.ReadResponse
读取HTTP响应函数：http.ReadResponse函数接受两个参数，一个是io.Reader类型（这里是前面创建的带缓冲的读取器bufio.NewReader(conn)），用于从其中读取HTTP响应数据，另一个是*http.Request类型（这里是创建的CONNECT请求对象）。这个函数会从读取器中解析HTTP响应，并返回一个http.Response结构体指针和一个可能的error值。
resp：如果读取和解析成功，resp将是一个指向http.Response结构体的指针，其中包含了服务器返回的响应信息，如状态码、响应头、响应体等。
err：如果在读取或解析过程中出现问题，err将是非nil的，可能的错误包括网络连接问题、HTTP协议解析错误等。



## 负载均衡

此处负载均衡采用随机选择和轮询两种，主要在客户端实现选择。

------

首先需要实现服务发现功能，指客户端能够发现哪些服务端可用，主要关注在网络上（不是动态发现哪些过程可调用，不过也是个很高级的功能）。说到这里，涉及到基本的服务注册和服务发现（前段时间课上提过），其实是需要一个注册中心和发现模块。

服务发现模块Discovery，最基本的接口有：

- `Refresh()`从注册中心获取可用列表
- `Update(servers []string)`手动更新服务发现的服务列表，注意是Discovery的服务可用列表
- `Get(mode SelectMode)`根据负载均衡策略获取一个可用服务实例
- `GetAll`返回所有服务实例

简化处理，先实现一个不需要注册中心，服务列表是手动维护的服务发现模块`MultiServersDiscovery`，它实现上述的所有接口。服务注册时使用的地址为`prot@address`，代表一个服务端

------

然后实现支持负载均衡的客户端，与通信模块解耦，此处是xclient，它同时拥有Discovery字段和clients字段，即服务发现和客户端复用（服务发现是客户端能够发现哪些服务端可用！为什么要记录客户端实例呢，是为了复用Socket连接，每一个客户端实例保存了一个到具体server的连接）

这部分的client复用有点绕，其在调用上封装得太好了，实际代码就一个Call或者BroadCast，但是事实上调用链路有点长。以Call为例，Call会调用Get发现server，再调用未导出的call，再用dial尝试获取client实例，如无对应连接可用的client，就创建一个可用于连接的client（xc.Call->xc.call->xc.dial->(client.XDial)->client.Call）。也就是Call的时候才尝试获取连接，不像之前的通信模块Client是先建立连接再调用，而是直接在调用Call时尝试连接，毕竟咱把连接存起来了。这种实现对实际调用RPC更透明了，封装的好！

xclient要实现的方法在上述调用已经基本体现了其功能，还要实现Broadcast调用所有服务端，只返回其中一个处理结果，一旦一个处理有错则返回错误。

Broadcast首先获取所有服务端的信息，设置`replyDone`用于记录reply是否已经填写了（我i们只要一份reply，先到先得），设置等待组和锁，设置上下文为可取消，然后并发地向不同服务端发请求并记录。

------

具体代码解释

```
rand.New(rand.NewSource(time.Now().UnixNano()))
```

`rand.NewSource(time.Now().UnixNano())`
创建随机数种子：rand.NewSource函数接受一个int64类型的值作为随机数生成的种子。time.Now().UnixNano()获取当前时间的纳秒数。使用当前时间的纳秒数作为种子有以下好处：
唯一性：每次程序运行时，当前时间的纳秒数几乎肯定是不同的（除非程序在同一纳秒内多次启动，这在实际情况中几乎不可能），这保证了每次运行生成的随机数序列有很大的差异。
随机性足够：纳秒级别的时间精度提供了一个范围很广的值域，能为随机数生成引入足够的随机性。
`rand.New(...)`
创建rand.Rand对象：rand.New函数接受一个rand.Source类型的参数（这里就是rand.NewSource(time.Now().UnixNano())的结果），并返回一个rand.Rand类型的对象。rand.Rand对象是用于生成随机数的实际对象，它基于传入的rand.Source所提供的种子信息，通过特定的算法来生成伪随机数序列。这个对象提供了多种生成不同类型随机数的方法，如Intn（生成指定范围内的整数随机数）等，在后续代码中可以使用这个对象来获取随机值。

```
d.r.Intn(math.MaxInt32 - 1)
```

Intn返回一个[0,math.MaxInt32 - 1]的数，防止轮询每次从0开始

```
ctx, cancel := context.WithCancel(ctx)
```

这个上下文的调用有点抽象，cancel只是用来关闭`ctx.Done`通道的，要想通知到协程关闭，需要协程主动监听这个通道，在收到信号后自行进行终止处理。也就是说context只是个协程间通信工具，并不能做什么。那么本文的cancel真正起作用的地方是在client.Call中，内含监听Done，调用cancel的时候它会收到信号自行终止，再反馈到Broadcast上。真是妙

## 服务发现与注册中心

注册中心作为一个独立于客户端和服务端的单独模块，作用是让服务端注册服务，客户端的服务发现组件能发现可用服务端。

Register

Discovery

## tcp粘包

1.先解决现有RPC框架中的TCP粘包问题

编解码的数据优先存储到缓存区，而不是直接传输，无法彻底解决粘包，在gob编解码出错，无法正确匹配类型Header和Body
rpc server: read header error: gob: type mismatch: no fields matched compiling decoder for Header
有个解决办法https://juejin.cn/post/6844903778219458567