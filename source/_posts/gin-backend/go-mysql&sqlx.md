---
title: go-mysql&sqlx
date: 2025-01-22 11:25:00
categories:
- bluebell
---
# go-sql

## 特性

go-sql的执行特性是query和exec执行完返回对数据库的链接，需要再执行Scan绑定到Go代码的变量中。因此需要**手动关闭**返回对数据库的链接，注意在错误判断后defer关闭。

## 连接

流程：`sql.Open`写入数据源但不连接，`db.Ping`尝试连接

```
func initDB() (err error) {
	dns := "user:password@tcp(127.0.0.1:3306)/sql_test"
	db, err = sql.Open("mysql", dns)
	if err != nil {
		return err
	}
	err = db.Ping()
	if err != nil {
		return err
	}
	return nil
}
```

**SetMaxOpenConns**

```go
func (db *DB) SetMaxOpenConns(n int)
```

`SetMaxOpenConns`设置与数据库建立连接的最大数目。 如果n大于0且小于最大闲置连接数，会将最大闲置连接数减小到匹配最大开启连接数的限制。 如果n<=0，不会限制最大开启连接数，默认为0（无限制）。

**SetMaxIdleConns**

```go
func (db *DB) SetMaxIdleConns(n int)
```

SetMaxIdleConns设置连接池中的最大闲置连接数。 如果n大于最大开启连接数，则新的最大闲置连接数会减小到匹配最大开启连接数的限制。 如果n<=0，不会保留闲置连接。

## 查询

查询一行用`db.QueryRow`，查多行用`db.Query`。

流程：查询一行：`db.Query.Scan`；查询多行：`db.Query->rows.Next->row.Sacn`

```
func queryRowDemo() {
	sqlstr := "select * from user where id = ?"
	var u user
	err := db.QueryRow(sqlstr, 1).Scan(&u.id, &u.name, &u.age)
	if err != nil {
		fmt.Printf("scan failed, err:%v\n", err)
		return
	}
	fmt.Printf("id:%d name:%s age:%d\n", u.id, u.name, u.age)
}

func queryMUltiRowDemo() {
	sqlstr := "select * from user where id > ?"
	rows, err := db.Query(sqlstr, 3)
	if err != nil {
		fmt.Printf("query failed, err:%v\n", err)
		return
	}
	defer rows.Close()
	for rows.Next() {
		var u user
		err := rows.Scan(&u.id, &u.name, &u.age)
		if err != nil {
			fmt.Printf("scan failed, err:%v\n", err)
			return
		}
		fmt.Printf("id:%d name:%s age:%d\n", u.id, u.name, u.age)
	}
}
```

## 插入、更新、删除

大差不差，都是用`db.Exec`

```
func insertRowDemo() {
	sqlstr := "insert into user(name,age) values (?,?)"
	ret, err := db.Exec(sqlstr, "will", 20)
	if err != nil {
		fmt.Println("insert failed, err:%V\n", err)
		return
	}
	theID, err := ret.LastInsertId()
	if err != nil {
		return
	}
	fmt.Printf("insert success,the is is %v", theID)
}

func updateRowDemo() {
	sqlstr := "update user set age=? where id = ?"
	res, err := db.Exec(sqlstr, 39, 3)
	if err != nil {
		fmt.Println("update failed, err", err)
		return
	}
	n, err := res.RowsAffected()
	if err != nil {
		fmt.Println("get RowsAffected failed, err", err)
		return
	}
	fmt.Println("update success,affectd rows:", n)
}

func deleteRowDemo() {
	sqlstr := "delete from user where id = ?"
	res, err := db.Exec(sqlstr, 3)
	if err != nil {
		fmt.Println("delete failed, err:", err)
		return
	}
	n, err := res.RowsAffected()
	if err != nil {
		fmt.Println("get RowsAffected failed, err", err)
		return
	}
	fmt.Println("delete success,affectd rows:", n)
}
```

## 预处理

提前传递命令语句给sql，后续再传递数据的行为。避免了重复执行SQL方法，提升性能。

流程：使用`db.Prepare`预先传递命令，在使用`stmt.Query`或`stmt.Exec`.

```
func prepareQueryDemo() {
	sqlstr := "select * from user where id > ?"
	stmt, err := db.Prepare(sqlstr)
	if err != nil {
		fmt.Printf("prepare failed, err:%v\n", err)
		return
	}
	defer stmt.Close()
	rows, err := stmt.Query(3)
	if err != nil {
		fmt.Printf("query failed, err:%v\n", err)
		return
	}
	defer rows.Close()
	for rows.Next() {
		var u user
		err := rows.Scan(&u.id, &u.name, &u.age)
		if err != nil {
			fmt.Printf("scan failed, err:%v\n", err)
			return
		}
		fmt.Printf("id:%d name:%s age:%d\n", u.id, u.name, u.age)
	}
}

func prepareInsertDemo() {
	sqlstr := "insert into user(name,age) values (?,?) "
	stmt, err := db.Prepare(sqlstr)
	if err != nil {
		fmt.Printf("prepare failed, err:%v\n", err)
		return
	}
	defer stmt.Close()
	res, err := stmt.Exec("小王子", 1)
	if err != nil {
		fmt.Printf("insert failed, err:%v\n", err)
		return
	} else {
		fmt.Println("res:", res)
	}

	res, err = stmt.Exec("华语", 32)
	if err != nil {
		fmt.Printf("insert failed, err:%v\n", err)
		return
	} else {
		fmt.Println("res:", res)
	}
	fmt.Println("insert success.")
}
```

## 事务

### 事务相关方法

Go语言中使用以下三个方法实现MySQL中的事务操作。

开始事务

```go
func (db *DB) Begin() (*Tx, error)
```

提交事务

```go
func (tx *Tx) Commit() error
```

回滚事务

```go
func (tx *Tx) Rollback() error
```

# sqlx

[sqlx库使用指南 | 李文周的博客 (liwenzhou.com)](https://www.liwenzhou.com/posts/Go/sqlx/#c-0-3-6)

[golang 数据库开发神器 sqlx使用指南 - 孙龙-程序员 - 博客园 (cnblogs.com)](https://www.cnblogs.com/sunlong88/p/13032231.html)

使用结构体记得导出（字段首字母大写）！

## 连接

关键函数Connect原型，`driverName`驱动名，`dataSourceName` 数据源，返回db指针

```go
func sqlx.Connect(driverName string, dataSourceName string) (*sqlx.DB, error)
```

```go
func initDB() (err error) {
	dsn := "user:password@tcp(127.0.0.1:3306)/sql_test?charset=utf8mb4&parseTime=True"
	// 也可以使用MustConnect连接不成功就panic
	db, err = sqlx.Connect("mysql", dsn)
	if err != nil {
		fmt.Printf("connect DB failed, err:%v\n", err)
		return
	}
	db.SetMaxOpenConns(20)
	db.SetMaxIdleConns(10)
	return
}
```

## 查询

Select提供查询结果的映射

```
Select(dest interface{}, query string, args ...interface{}) error
```

Select执行语句后直接绑定到参数

```
err := db.Select(&users, sqlStr, 0)
```

## 插入、更新、删除

Exec只返回sql.Result，没有处理映射

```
Exec(query string, args ...any) (sql.Result, error)
```

## NamedExec

`DB.NamedExec`方法用来绑定SQL语句与结构体或map中的同名字段。也就是使用同名字段的方式来传递原先占位符需要传递的参数。sql语句中的(:name,:age)指明了同名参数。

```
NamedExec(query string, arg interface{}) (sql.Result, error)
```

```
func insertUserDemo()(err error){
	sqlStr := "INSERT INTO user (name,age) VALUES (:name,:age)"
	_, err = db.NamedExec(sqlStr,
		map[string]interface{}{
			"name": "七米",
			"age": 28,
		})
	return
}
```

## NamedQuery

与`DB.NamedExec`同理

## 事务

对于事务操作，我们可以使用`sqlx`中提供的`db.Beginx()`和`tx.Exec()`方法

这部分挺有意思的

```
defer func() {
		if p := recover(); p != nil {
			tx.Rollback() // 1. If a panic occurs, rollback the transaction.
			panic(p)      // 2. Re-panic to allow further handling or propagation.
		} else if err != nil {
			fmt.Println("err:", err)
			fmt.Println("rollback") // 3. If an error occurred, print "rollback".
			tx.Rollback()           // 4. Rollback the transaction.
		} else {
			err = tx.Commit()     // 5. If no error, try to commit the transaction.
			fmt.Println("commit") // 6. Print "commit" after a successful commit.
		}
	}()
```



```
func tranctionDemo2() (err error) {
	tx, err := db.Begin()
	if err != nil {
		fmt.Printf("begin trans failed, err:%v\n", err)
		return err
	}
	defer func() {
		if p := recover(); p != nil {
			tx.Rollback() // 1. If a panic occurs, rollback the transaction.
			panic(p)      // 2. Re-panic to allow further handling or propagation.
		} else if err != nil {
			fmt.Println("err:", err)
			fmt.Println("rollback") // 3. If an error occurred, print "rollback".
			tx.Rollback()           // 4. Rollback the transaction.
		} else {
			err = tx.Commit()     // 5. If no error, try to commit the transaction.
			fmt.Println("commit") // 6. Print "commit" after a successful commit.
		}
	}()
	sqlStr1 := "Update user set age=30 where id =?"
	rs, err := tx.Exec(sqlStr1, 1)
	if err != nil {
		return err
	}
	n, err := rs.RowsAffected()
	if err != nil {
		return err
	}
	if n != 1 {
		return errors.New("exec sqlStr1 failed")
	}
	sqlStr2 := "Update user set age=50 where id=?"
	rs, err = tx.Exec(sqlStr2, 5)
	if err != nil {
		return err
	}
	n, err = rs.RowsAffected()
	if err != nil {
		return err
	}
	if n != 1 {
		return errors.New("exec sqlStr1 failed")
	}
	return nil

}
```

## sqlx.In



实现批量插入

```
func (u user) Value() (driver.Value, error) {
	return []interface{}{u.Name, u.Age}, nil
}

func BatchInsertUser2(user []interface{}) error {
	query, args, _ := sqlx.In(
		"INSERT INTO user (name, age) VALUES (?), (?), (?)",
		user...,
	)
	fmt.Println(query) // 查看生成的querystring
	fmt.Println(args)  // 查看生成的args
	_, err := db.Exec(query, args...)
	return err
}
```

当然使用namedExec也可以



实现批量查询:

sqlx默认使用?占位，Rebind根据当前数据库驱动重新生成占位符。

```
// QueryByIDs 根据给定ID查询
func QueryByIDs(ids []int)(users []User, err error){
	// 动态填充id
	query, args, err := sqlx.In("SELECT name, age FROM user WHERE id IN (?)", ids)
	if err != nil {
		return
	}
	// sqlx.In 返回带 `?` bindvar的查询语句, 我们使用Rebind()重新绑定。
	// 重新生成对应数据库的查询语句（如PostgreSQL 用 `$1`, `$2` bindvar）
	query = DB.Rebind(query)

	err = DB.Select(&users, query, args...)
	return
}

```





### **`sqlx.In` 的作用**

在 SQL 查询中，如果需要使用 `IN` 子句来匹配多条记录，通常会面临一个问题：  
- **如何动态填充 `IN` 子句中的参数？**
  

直接拼接字符串是不安全的，并可能引发 **SQL 注入风险**。`sqlx.In` 解决了这个问题。

---

### **`sqlx.In` 的主要功能**
1. **安全地处理 `IN` 子句中的多个参数**。
2. **将切片/数组作为参数展开**，动态生成 SQL 查询。
3. **返回 SQL 语句及参数数组**，以供后续执行查询。

---

### **示例：`sqlx.In` 的用法**

```go
ids := []int{1, 2, 5}

// 使用 sqlx.In 生成 SQL 查询和参数
query, args, err := sqlx.In("SELECT name, age FROM user WHERE id IN (?)", ids)
if err != nil {
    fmt.Printf("sqlx.In failed: %v\n", err)
    return
}
fmt.Println("Query:", query)
fmt.Println("Args:", args)
```

**输出：**
```
Query: SELECT name, age FROM user WHERE id IN (?, ?, ?)
Args: [1 2 5]
```

#### **解释**
- `sqlx.In` 将数组 `ids` 展开为多个占位符，并生成 SQL 语句：  
  `SELECT name, age FROM user WHERE id IN (?, ?, ?)`
- 返回的参数数组为 `[1, 2, 5]`，可用于绑定到查询语句。

---

### **为什么需要 `sqlx.In`？**

1. **解决 SQL 查询的动态参数问题：**
   - 在 `IN` 子句中，参数的数量不固定（如用户输入多个 ID），难以提前确定。
   - 传统拼接字符串会导致 **SQL 注入** 风险。

2. **简化多参数查询：**
   - 不需要手动拼接占位符（如 `(?, ?, ?)`）。
   - 避免了代码中的复杂逻辑。

3. **确保查询的安全性：**
   - 使用参数绑定的方式代替字符串拼接，防止 SQL 注入。

---

### **和 `Rebind` 的配合**

`sqlx.In` 使用 **`?`** 作为占位符，但某些数据库（如 PostgreSQL）使用 **`$1, $2`** 等占位符格式。  
这时需要用 **`DB.Rebind()`** 将占位符重新格式化，以匹配具体的数据库驱动。

---

### **完整代码示例**

```go
func QueryByIDs(ids []int) ([]User, error) {
    // 使用 sqlx.In 生成 SQL 语句和参数
    query, args, err := sqlx.In("SELECT name, age FROM user WHERE id IN (?)", ids)
    if err != nil {
        return nil, err
    }

    // 重新绑定占位符，匹配数据库驱动
    query = DB.Rebind(query)

    // 执行查询并映射结果到 users 切片中
    var users []User
    err = DB.Select(&users, query, args...)
    return users, err
}
```

---

### **总结**

- **`sqlx.In`** 是一种简洁、安全的方式，用于处理动态参数（如数组、切片）在 SQL 查询中的 `IN` 子句。
- 它避免了手动拼接 SQL 字符串，降低了代码复杂性和 SQL 注入的风险。
- **结合 `Rebind`** 使用时，可以确保生成的查询语句符合不同数据库驱动的规范。

## Get和Select

在 `sqlx` 包中，`Get` 和 `Select` 是用于执行查询并将结果映射到 Go 结构体的两个方法。以下是对每个方法的详细解释：

### 1. `Get`

**签名：**
```go
func (db *DB) Get(dest interface{}, query string, args ...interface{}) error
```

**描述：**
- `Get` 方法用于执行一个 SQL 查询，该查询预期返回单行结果。
- 它将查询结果扫描到提供的目标变量 `dest` 中，`dest` 应该是指向结构体或与返回行的列匹配的类型的指针。

**使用示例：**
```go
type User struct {
    ID   int    `db:"id"`
    Name string `db:"name"`
    Age  int    `db:"age"`
}

var user User
err := db.Get(&user, "SELECT * FROM users WHERE id = ?", 1)
if err != nil {
    // 处理错误
}
fmt.Printf("User: %+v\n", user)
```

### 2. `Select`

**签名：**
```go
func (db *DB) Select(dest interface{}, query string, args ...interface{}) error
```

**描述：**
- `Select` 方法用于执行一个 SQL 查询，该查询可能返回多行结果。
- 它将查询结果扫描到提供的目标变量 `dest` 中，`dest` 应该是指向结构体切片或数组的指针。

**使用示例：**
```go
var users []User
err := db.Select(&users, "SELECT * FROM users WHERE age > ?", 18)
if err != nil {
    // 处理错误
}
fmt.Printf("Users: %+v\n", users)
```

### 关键区别

- **结果预期：**
  - `Get`：预期返回单行结果（如果没有找到行则返回错误）。
  - `Select`：预期返回多行结果（结果返回为切片）。

- **目标类型：**
  - `Get`：`dest` 应该是结构体的指针。
  - `Select`：`dest` 应该是结构体切片的指针。

### 错误处理
这两种方法都会在查询失败、未找到结果（对于 `Get`）或将结果扫描到目标中失败时返回错误。

### 两种方法的完整示例

以下是一个完整示例，展示如何在一个使用 `sqlx` 的 Go 程序中使用这两种方法：

```go
package main

import (
    "fmt"
    "log"

    _ "github.com/go-sql-driver/mysql"
    "github.com/jmoiron/sqlx"
)

type User struct {
    ID   int    `db:"id"`
    Name string `db:"name"`
    Age  int    `db:"age"`
}

var db *sqlx.DB

func initDB() {
    dsn := "root:password@tcp(127.0.0.1:3306)/testdb"
    var err error
    db, err = sqlx.Connect("mysql", dsn)
    if err != nil {
        log.Fatalf("连接数据库失败: %v", err)
    }
}

func main() {
    initDB()
    
    // 使用 Get 获取单个用户
    var user User
    err := db.Get(&user, "SELECT * FROM users WHERE id = ?", 1)
    if err != nil {
        log.Fatalf("获取用户失败: %v", err)
    }
    fmt.Printf("单个用户: %+v\n", user)

    // 使用 Select 获取多个用户
    var users []User
    err = db.Select(&users, "SELECT * FROM users WHERE age > ?", 18)
    if err != nil {
        log.Fatalf("选择用户失败: %v", err)
    }
    fmt.Printf("年龄大于18的用户: %+v\n", users)
}
```

### 总结

- **`Get`** 和 **`Select`** 是 `sqlx` 中的基本方法，用于执行查询并将结果映射到 Go 类型。
- 它们简化了从数据库中获取数据的过程，使代码更简洁并且更安全，避免了 SQL 注入攻击。
