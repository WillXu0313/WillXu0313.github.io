---
title: HTTP状态码
date: 2025-01-22 11:25:00
categories:
- bluebell
---
# HTTP状态码

[HTTP常见状态码 && HTTP的逐步发展（通俗易懂版）_网络请求码418-CSDN博客](https://blog.csdn.net/ScheenDuan/article/details/142343622#:~:text=HTTP 状态码 是)

HTTP 状态码是一组由服务器返回给客户端的标准响应代码，用来表示 HTTP 请求的状态。它们帮助客户端了解请求的结果，是 Web 应用开发中不可或缺的一部分。

HTTP 状态码由三位数字组成，按照用途和语义可以分为五个主要的类别：

## 1xx: 信息性状态码（Informational Responses）
1xx 状态码表示请求已经被接收，客户端可以继续发送请求。

- **100 Continue**: 表示客户端可以继续发送请求的剩余部分（比如，POST 请求的主体部分）。
- **101 Switching Protocols**: 表示服务器同意客户端的协议切换请求（如 HTTP 切换到 WebSocket）。
- **102 Processing (WebDAV)**: 表示服务器正在处理请求，还没有完成。

## 2xx: 成功状态码（Successful Responses）
2xx 状态码表示请求已经成功被服务器接收、理解并处理。

- **200 OK**: 请求成功，服务器返回了请求的资源（通常是 `GET` 请求的响应）。
- **201 Created**: 请求成功并且服务器创建了新的资源（通常是 `POST` 请求的响应）。
- **202 Accepted**: 请求已经被接受，但尚未处理。通常用于异步操作。
- **204 No Content**: 请求成功，但服务器没有返回任何内容。通常用于 `DELETE` 请求。
- **206 Partial Content**: 表示服务器只返回了部分内容（如文件分块下载）。

## 3xx: 重定向状态码（Redirection Responses）
3xx 状态码表示需要进一步操作才能完成请求，通常用于 URL 重定向。

- **301 Moved Permanently**: 资源的 URL 已永久更改，客户端应将请求重定向到新 URL。
- **302 Found**: 临时重定向，资源的 URL 已更改，但客户端应继续使用原始 URL 发出未来的请求。
- **303 See Other**: 客户端应当使用 `GET` 请求重新获取资源（用于避免重复的 `POST` 操作）。
- **304 Not Modified**: 表示客户端有缓存的版本且该版本未修改，允许客户端使用缓存版本。
- **307 Temporary Redirect**: 临时重定向，客户端应使用原始的 HTTP 方法重新请求新地址。
- **308 Permanent Redirect**: 永久重定向，客户端应使用原始 HTTP 方法请求新地址。

## 4xx: 客户端错误状态码（Client Errors）
4xx 状态码表示客户端的请求存在错误，服务器无法处理。

- **400 Bad Request**: 请求格式错误或无效参数。
- **401 Unauthorized**: 请求未通过认证，客户端需要提供有效的身份认证信息。
- **403 Forbidden**: 请求被服务器拒绝，客户端无权限访问该资源。
- **404 Not Found**: 请求的资源不存在或找不到。
- **405 Method Not Allowed**: 请求使用了服务器不允许的 HTTP 方法。
- **406 Not Acceptable**: 服务器无法生成客户端能接受的内容。
- **408 Request Timeout**: 客户端在规定时间内没有发送请求，导致请求超时。
- **409 Conflict**: 请求无法处理，因为它与当前资源的状态冲突（如重复的更新）。
- **410 Gone**: 请求的资源永久不可用，且没有新地址。
- **413 Payload Too Large**: 请求体内容过大，服务器无法处理。
- **415 Unsupported Media Type**: 请求中的媒体类型不受支持（例如上传的文件格式错误）。
- **429 Too Many Requests**: 客户端发送了过多的请求，被限流。

## 5xx: 服务器错误状态码（Server Errors）
5xx 状态码表示服务器在处理请求时发生了错误，无法完成请求。

- **500 Internal Server Error**: 服务器遇到了意外情况，无法完成请求。
- **501 Not Implemented**: 服务器不支持当前请求的方法，或者不具备处理的能力。
- **502 Bad Gateway**: 作为网关或代理的服务器从上游服务器接收到无效响应。
- **503 Service Unavailable**: 服务器当前无法处理请求，通常是由于维护或过载。
- **504 Gateway Timeout**: 作为网关或代理的服务器没有及时从上游服务器接收到响应。
- **505 HTTP Version Not Supported**: 服务器不支持客户端请求的 HTTP 协议版本。

## 常见 HTTP 状态码的解释与使用场景

1. **200 OK**: 
   - **场景**: `GET` 请求成功，服务器返回了资源。
   - **例子**: 用户成功访问一个网页或获取某个数据。

2. **201 Created**:
   - **场景**: `POST` 请求成功，服务器创建了一个新资源。
   - **例子**: 用户成功注册，创建了一个新账户。

3. **400 Bad Request**:
   - **场景**: 客户端发送的请求格式有问题，服务器无法理解。
   - **例子**: API 请求中参数缺失或格式错误。

4. **401 Unauthorized**:
   - **场景**: 请求未通过身份验证。
   - **例子**: 用户未登录或登录凭证过期，访问受限资源。

5. **403 Forbidden**:
   - **场景**: 请求被拒绝，客户端没有权限访问资源。
   - **例子**: 试图访问管理员专用的页面，但用户没有管理员权限。

6. **404 Not Found**:
   - **场景**: 请求的资源在服务器上不存在。
   - **例子**: 用户访问一个不存在的 URL。

7. **500 Internal Server Error**:
   - **场景**: 服务器端发生错误，无法完成请求。
   - **例子**: 代码运行时遇到未处理的异常。

8. **503 Service Unavailable**:
   - **场景**: 服务器暂时过载或正在维护。
   - **例子**: 在高峰期服务器资源不足时，无法处理请求。

## 如何选择合适的 HTTP 状态码
- **成功类（2xx）**: 如果请求正常处理完毕，比如数据获取、创建或修改，都应该使用 2xx 的状态码，最常见的是 `200 OK`。
- **重定向类（3xx）**: 如果资源被移到新的地址或者请求需要进一步操作，使用 3xx 状态码，例如 `301 Moved Permanently` 或 `302 Found`。
- **客户端错误类（4xx）**: 当请求有误时，返回 4xx 状态码，最常见的有 `400 Bad Request`（请求格式有误）和 `404 Not Found`（请求的资源不存在）。
- **服务器错误类（5xx）**: 如果问题发生在服务器端，比如代码出错、数据库连接失败等，则返回 5xx 状态码，比如 `500 Internal Server Error` 或 `503 Service Unavailable`。

## 总结
HTTP 状态码是客户端与服务器通信中不可或缺的一部分，通过状态码可以快速了解请求的结果以及是否需要进一步处理。理解和正确使用状态码不仅能够提升 API 的可用性，还能让客户端开发人员更快地发现和解决问题。