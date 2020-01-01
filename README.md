# Server Hub

[pypi](https://pypi.org/project/serverhub/0.0.1/)

Server Hub 服务端 + 工具。

1. Server Hub 服务器，在被监控机器上，收集信息，响应客户端查询。通过证书验证客户端身份。
2. 证书生成工具

目前只支持 Linux 系统，和 Python 3（但是 python 2 可能也行，没测）

## 安装

直接使用 pip 安装

`pip install serverhub`

---
如果有问题可以使用 pypi 源

`pip install -i https://pypi.org/simple serverhub`

如果你没有 root 权限，可以添加 `--user` 参数即

`pip install serverhub --user` 或
`pip install -i https://pypi.org/simple serverhub` --user`

另外在某些比较旧版本系统上 pip 指向 pip2，所以需要使用 pip3 代替命令中的 pip

## 使用

- 启动监控服务器 `serverhub -s -c /home/user/.serverhub/server` 
  - 默认端口是 12345，可以使用 `-p` 参数指定端口。 
  - `-c` 参数指定服务器使用的证书和密钥的路径，证书和密钥的名称应该相同，例如例子中，证书是 /home/user/.serverhub/server.crt，密钥是 /home/user/.serverhub/server.pem。

- 生成根证书 `serverhub -r`
  - 将要求从输入证书名称，默认是 ca
  - 可以使用 `-t` 指定存放证书的目录，默认是 ~/.serverhub
  - 可以使用 `-d` 指定证书有效期，默认是 365 天
- 使用已有证书签发新证书 `serverhub -c  ~/.serverhub/ca`
  - 可以使用 `-t` 指定存放证书的目录，默认是 ~/.serverhub
  - 可以使用 `-d` 指定证书有效期，默认是 365 天



### 全部参数

```
Usage: serverhub -r|-s|-c  [-p <port>] [-d <days>] [-t <target path>]
    -s                start server
    -p <port>         default is 12345
    -t <target dir>   
    -r                make a root cert
    -d <days>         default is 365
    -c <cert path>    make a cert for client, or used with -s to set cert path
Examples:
    serverhub -r
         make a root cert and pem to ~/.serverhub/, you can input a name for it by stdin
    serverhub -c  ~/.serverhub/ca
         make a cert signed with ~/.serverhub/ca.cert
    serverhub -s -p 8000 -c ~/.serverhub/server
         start server at 0.0.0.0:8000, use ~/.serverhub/server.cert and ~/.serverhub/server.pem
```

`-s` 启动服务器，必须使用 `-c` 指定证书、密钥的名称。证书、密钥必须同路径、同名，扩展名分别为 crt 和 pem

`-r` 生成根证书（自签名证书），可选参数 `-t`、`-d`，执行命令后将从标准输入输入证书名。回生成两个文件，一个 crt 文件是证书，一个 pem 文件是密钥

`-c` 签名新证书，必须指定签名证书、密钥的名称。证书、密钥必须同路径、同名，扩展名分别为 crt 和 pem。可选参数 `-t`、`-d`，执行命令后将从标准输入输入新证书名。会生成三个文件，一个 crt 文件是证书，一个 pem 文件是密钥（python 用），一个 java.pem 文件，是给 Android 使用的密钥。

`-p` 与 `-s` 一起使用，指定监听端口号，默认 12345

`-t` 与 `-r`或者`-c`配合使用，用于指定新证书和密钥的存放路径

`-d` 与 `-r`或者`-c`配合使用，用于指定新证书的有效期，一个整数，代表天数