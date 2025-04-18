---
title: URL编码
date: 2025-04-19 07:11:14
categories:
- Else
---

# URL编码

参考：

[URL是什么意思 ？ URL介绍](https://blog.csdn.net/chen1415886044/article/details/103914255)

https://www.runoob.com/tags/html-urlencode.html

https://www.toolhelper.cn/EncodeDecode/Url

## 为什么了解这个东西？

因为在项目中遇到了问题——使用curl带data-urlencode转换参数后发送请求，请求被正确处理。而将所有参数直接抄送到URL链接上，然后发送，请求没有被正确处理。如下：

```bash
curl --get "http://172.34.1.2:8080/zstack/externalapi/runinstances" \
     --data-urlencode "Action=RunInstances" \
     --data-urlencode "AccessKeyId=5JTCsycG8njeJ5gnRl1I" \
     --data-urlencode "Signature=5OFxfJ2nc5Z3QeTfgDygBCe3W2k=" \
     --data-urlencode "UserData=I3Bvd2Vyc2hlbGwKCiMgKioqKioqKioqKioqKioq+++"

//验签通过
{"Message":"Failed to create one or more instance, details: field[l3NetworkUuids] cannot contain any null element","RequestId":"88a6925a77c64048a8a33f4498842e9a","Code":"CreateInstanceFailed"}   
```

```bash
http://172.34.1.2:8080/zstack/externalapi/RunInstances?Action=RunInstances&AccessKeyId=5JTCsycG8njeJ5gnRl1I&Signature=5OFxfJ2nc5Z3QeTfgDygBCe3W2k=&UserData=I3Bvd2Vyc2hlbGwKCiMgKioqKioqKioqKioqKioq+++

//验签没通过
{"Message":"The specified parameter \"Signature\" is not valid. The signature is not valid.","RequestId":"09ee04f3364b46a8b14d1236d4143624","Code":"InvalidParameter"}
```

为了解决这个问题，于是结合已知信息和搜索引擎，了解到URL编码。

上述URL之所以验签失败，是因为参数值中包含特殊字符`+`、`=`，**没有提前进行URL编码**，导致参数值没有被服务器正确解析，例如 `+` 在URL中默认被服务器解析为空格，进而导致生成错误的校验签名，导致验签失败。

而使用curl命令时使用--data-urlencode进行了url编码，保证了所有参数值能被服务器正确解析，所以服务器能生成正确的校验签名，验签能够通过。

综上，解决上述问题，正确做法是在拼接URL时提前对参数值进行严格URL编码，确保特殊字符被正确编码。

## URL组成

URL的一般语法格式为：

```
protocol :// hostname[:port] / path / [?query]#fragment
```

- protocol：协议，例如http、https
- hostname：主机名（域名、IP地址）
- port：端口
- path：路径
- query：查询字符串，是通过`&`分割的键值对列表，遵循形式`key=value`，例如http://www.haha.com/test/?a=1&b=2
- fragment：片段（锚点），用于页面跳转

保留字符

| 字符 | 功能                 | 示例                             |
| ---- | -------------------- | -------------------------------- |
| `?`  | 查询字符串的起始标志 | `https://example.com/?key=value` |
| `&`  | 参数分隔符           | `key1=value1&key2=value2`        |
| `=`  | 键值对分隔符         | `key=value`                      |
| `/`  | 路径分隔符           | `https://example.com/path/to`    |
| `#`  | 片段标识符           | `https://example.com/#section1`  |
| `+`  | 空格的替代符号       | `query=Java+Script`              |

## 什么是URL编码？

URL编码，又称为百分号编码，Percent-Encoding，指的是在%后跟两位16进制数来表示字符，例如`%20`表示空格，`%2B`表示`+`。URL编码主要作用范围是参数值，但在路径、参数名等地方也适用。

## 为什么需要URL编码？

1. URL只能使用ASCII字符集来通过因特网进行发送（历史问题？安全性？标准化？怎么个注入攻击的可能啊啊？），有表达ASCII之外的字符的需求。具体如何表达，是将非ASCII字符按照编码方式转换为字节序列，然后对每个字节值前加上%号（没有很懂，需要补充）。
2. URL本身有**保留字符**`?`, `&`, `=`, `/`, `#`，`+`，这些字符在URL中有特殊的含义（什么特殊含义啊？），用于分割不同的部分或者参数。如果参数值中直接包含这部分保留字符，会导致URL解析错误，所以需要对参数数值进行编码

## 具体编码规定

百分号编码只适用于非 ASCII 字符和某些保留字符（如 `?`, `&`, `=` 等）

1. 确定字符的Unicode码点
2. 将Unicode码点通过特定的字符编码方式表达为字节序列，字符编码大方式通常是UTF-8
3. 每个字节前加上%后拼接

例如：中的码点为U+4E2D，UTF-8表达为字节序列是E4 B8 AD，每个字节前加上%就完成了百分号编码

## 问题

https://www.runoob.com/try/html_form_submit.php?text=%E4%BD%A0%E5%A5%BD%20%E5%B8%A7+++ 这里我敲的空格直接被浏览器编码为%20，而显示实际发出的请求数据是text=%E4%BD%A0%E5%A5%BD+%E5%B8%A7+++，也就是说在发送数据的时候又被转义为+，+在URL中才表示空格，+号在请求发送前不会被转义。%20会被直接预先处理为+表示空格，那么真实的+号怎么被处理的？真实的+依赖于手动编码，避免被误认为是空格。这里有点绕，主要是浏览器的行为我搞不懂它的转换标准。

浏览器框、真实数据、发送请求数据，这三者是存在差异的。