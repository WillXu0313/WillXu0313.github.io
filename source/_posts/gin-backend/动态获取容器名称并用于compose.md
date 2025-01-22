---
title: docker-compose部署nginx + mysql + gin
date: 2025-01-22 11:25:00
categories:
- bluebell
---
在 Docker 中，**自动生成的容器名称**可以通过几种方式获取并在 `docker-compose.yml` 文件中使用。以下是几种常见的场景和解决方案：

### 1. **通过 `container_name` 指定容器名**
虽然 Docker 默认会为每个容器生成一个随机的名称，但你可以通过在 `docker-compose.yml` 文件中使用 `container_name` 来显式地指定容器名称。这是最常见和简单的做法。

#### 示例 `docker-compose.yml`：
```yaml
version: '3'
services:
  web:
    image: nginx
    container_name: my_web_container  # 这里指定容器名称
    ports:
      - "8080:80"
  db:
    image: mysql
    container_name: my_db_container   # 这里指定另一个容器名称
    environment:
      MYSQL_ROOT_PASSWORD: example
```

### 2. **使用 `docker-compose` 服务名称**
`docker-compose` 会根据服务名称自动生成容器名称，遵循以下格式：

```
<项目名>_<服务名>_<序号>
```

- `<项目名>`：默认是当前目录名，你可以通过 `-p` 参数或 `COMPOSE_PROJECT_NAME` 环境变量指定。
- `<服务名>`：`docker-compose.yml` 文件中定义的服务名称。
- `<序号>`：当服务扩展为多个容器时，这个序号会标识每个容器。

#### 示例 `docker-compose.yml`：
```yaml
version: '3'
services:
  web:
    image: nginx
    ports:
      - "8080:80"
  db:
    image: mysql
    environment:
      MYSQL_ROOT_PASSWORD: example
```

在默认情况下，`docker-compose` 生成的容器名称将是：
- `myproject_web_1` （假设项目名为 `myproject`）
- `myproject_db_1`

你可以通过使用这个命名规则在其他服务中引用这些容器。

### 3. **通过环境变量在 `docker-compose.yml` 中获取容器名称**
Docker 生成的容器名可以通过环境变量使用，但是如果你需要自动获取容器的名字，最常用的方式是通过 Docker 的命令行工具获取。

你可以使用以下命令获取容器名称：
```bash
docker ps --filter "name=<服务名>" --format "{{.Names}}"
```

### 4. **动态获取容器名称并传递给 `docker-compose.yml`**
虽然 `docker-compose.yml` 文件本身不支持动态执行脚本获取容器名称，但你可以通过在启动容器之前使用 shell 脚本或 `makefile` 来获取容器名称并将其传递给 `docker-compose.yml` 文件中的某些部分。你可以通过环境变量的方式传递容器名称。

#### 通过 Shell 脚本传递容器名称
```bash
#!/bin/bash
container_name=$(docker ps --filter "ancestor=my_image" --format "{{.Names}}")

export CONTAINER_NAME=$container_name
docker-compose up
```

然后在 `docker-compose.yml` 中使用：
```yaml
version: '3'
services:
  web:
    image: nginx
    container_name: ${CONTAINER_NAME}
```

### 总结
- 最简单的方式是在 `docker-compose.yml` 中手动指定容器名。
- 你也可以通过服务名称和 Docker 默认的命名规则来确定容器名。
- 如果需要动态获取容器名，可以借助 Shell 脚本或其他预处理机制，将容器名传递到 `docker-compose.yml` 中。
- 在 Docker 中，**自动生成的容器名称**可以通过几种方式获取并在 `docker-compose.yml` 文件中使用。以下是几种常见的场景和解决方案：

  ### 1. **通过 `container_name` 指定容器名**
  虽然 Docker 默认会为每个容器生成一个随机的名称，但你可以通过在 `docker-compose.yml` 文件中使用 `container_name` 来显式地指定容器名称。这是最常见和简单的做法。

  #### 示例 `docker-compose.yml`：
  ```yaml
  version: '3'
  services:
    web:
      image: nginx
      container_name: my_web_container  # 这里指定容器名称
      ports:
        - "8080:80"
    db:
      image: mysql
      container_name: my_db_container   # 这里指定另一个容器名称
      environment:
        MYSQL_ROOT_PASSWORD: example
  ```

  ### 2. **使用 `docker-compose` 服务名称**
  `docker-compose` 会根据服务名称自动生成容器名称，遵循以下格式：

  ```
  <项目名>_<服务名>_<序号>
  ```

  - `<项目名>`：默认是当前目录名，你可以通过 `-p` 参数或 `COMPOSE_PROJECT_NAME` 环境变量指定。
  - `<服务名>`：`docker-compose.yml` 文件中定义的服务名称。
  - `<序号>`：当服务扩展为多个容器时，这个序号会标识每个容器。

  #### 示例 `docker-compose.yml`：
  ```yaml
  version: '3'
  services:
    web:
      image: nginx
      ports:
        - "8080:80"
    db:
      image: mysql
      environment:
        MYSQL_ROOT_PASSWORD: example
  ```

  在默认情况下，`docker-compose` 生成的容器名称将是：
  - `myproject_web_1` （假设项目名为 `myproject`）
  - `myproject_db_1`

  你可以通过使用这个命名规则在其他服务中引用这些容器。

  ### 3. **通过环境变量在 `docker-compose.yml` 中获取容器名称**
  Docker 生成的容器名可以通过环境变量使用，但是如果你需要自动获取容器的名字，最常用的方式是通过 Docker 的命令行工具获取。

  你可以使用以下命令获取容器名称：
  ```bash
  docker ps --filter "name=<服务名>" --format "{{.Names}}"
  ```

  ### 4. **动态获取容器名称并传递给 `docker-compose.yml`**
  虽然 `docker-compose.yml` 文件本身不支持动态执行脚本获取容器名称，但你可以通过在启动容器之前使用 shell 脚本或 `makefile` 来获取容器名称并将其传递给 `docker-compose.yml` 文件中的某些部分。你可以通过环境变量的方式传递容器名称。

  #### 通过 Shell 脚本传递容器名称
  ```bash
  #!/bin/bash
  container_name=$(docker ps --filter "ancestor=my_image" --format "{{.Names}}")
  
  export CONTAINER_NAME=$container_name
  docker-compose up
  ```

  然后在 `docker-compose.yml` 中使用：
  ```yaml
  version: '3'
  services:
    web:
      image: nginx
      container_name: ${CONTAINER_NAME}
  ```

  ### 总结
  - 最简单的方式是在 `docker-compose.yml` 中手动指定容器名。
  - 你也可以通过服务名称和 Docker 默认的命名规则来确定容器名。
  - 如果需要动态获取容器名，可以借助 Shell 脚本或其他预处理机制，将容器名传递到 `docker-compose.yml` 中。