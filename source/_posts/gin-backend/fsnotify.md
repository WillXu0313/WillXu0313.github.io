---
title: fsnotify 文件系统通知库
date: 2025-01-22 11:25:00
categories:
- bluebell
---

`fsnotify` 是一个用于 Go 语言的文件系统通知库，它可以监视文件或目录的变化，比如文件的创建、删除、修改等。通过 `fsnotify`，你可以在文件系统发生变化时做出相应的响应，非常适合用于配置文件热加载、日志监控等场景。

### 常见应用场景
1. **配置文件热加载**：当配置文件发生变化时自动重新加载配置，不需要手动重启程序。
2. **日志监控**：监控日志文件是否被修改，实时获取日志变化。
3. **文件监控**：对文件的创建、删除、修改等操作进行监控并作出相应处理。

### 使用示例
以下是一个使用 `fsnotify` 监控配置文件变化的简单示例：

```go
package main

import (
	"fmt"
	"log"
	"github.com/fsnotify/fsnotify"
)

func main() {
	// 创建一个新的文件监控器
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer watcher.Close()

	// 启动一个 goroutine 来处理文件系统事件
	go func() {
		for {
			select {
			// 监听文件事件
			case event := <-watcher.Events:
				fmt.Printf("Event: %s\n", event)
				if event.Op&fsnotify.Write == fsnotify.Write {
					fmt.Printf("Modified file: %s\n", event.Name)
				}
			// 监听错误事件
			case err := <-watcher.Errors:
				fmt.Printf("Error: %s\n", err)
			}
		}
	}()

	// 添加需要监控的文件或目录
	err = watcher.Add("config.yaml")
	if err != nil {
		log.Fatal(err)
	}

	// 阻塞主程序，以免结束
	select {}
}
```

### 代码解析
- **`fsnotify.NewWatcher()`**：创建一个新的文件监视器。
- **`watcher.Add("config.yaml")`**：指定需要监控的文件或目录，这里监控的是 `config.yaml` 文件。
- **事件处理**：
  - `event.Op&fsnotify.Write == fsnotify.Write`：当文件发生写入修改时，触发对应的逻辑处理。
  - 可以根据 `event.Op` 判断是文件的创建、删除、重命名还是修改。

### 常见的事件类型
- `fsnotify.Create`：文件或目录被创建。
- `fsnotify.Remove`：文件或目录被删除。
- `fsnotify.Rename`：文件或目录被重命名。
- `fsnotify.Write`：文件或目录被修改。
- `fsnotify.Chmod`：文件权限被更改。

### 使用场景示例：配置文件热加载
假设你有一个配置文件 `config.yaml`，每次修改它时，你希望自动重新加载这个配置文件，`fsnotify` 可以帮你做到这一点。结合 `viper` 可以实现自动重新加载配置：

```go
package main

import (
	"fmt"
	"log"
	"time"

	"github.com/fsnotify/fsnotify"
	"github.com/spf13/viper"
)

func main() {
	// 设置配置文件
	viper.SetConfigFile("config.yaml")

	// 读取配置文件
	if err := viper.ReadInConfig(); err != nil {
		log.Fatalf("Error reading config file: %s\n", err)
	}

	// 监控配置文件变化并重新加载
	viper.WatchConfig()
	viper.OnConfigChange(func(e fsnotify.Event) {
		fmt.Printf("Config file changed: %s\n", e.Name)
	})

	// 阻塞程序，保持运行状态
	for {
		time.Sleep(10 * time.Second)
	}
}
```

### 总结
- `fsnotify` 提供了一种简单的方法来监控文件和目录的变化，适用于实时响应文件系统事件的场景。
- 通过 `fsnotify`，你可以实现配置文件的热加载、日志监控等功能，提高程序的灵活性和自动化能力。