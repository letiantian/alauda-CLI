Exec
---

该命令类似Docker下的exec，不过这里是在远程的灵雀云的容器中执行命令。

## 依赖
在Linux、Mac系统中请先安装ssh程序；在Windows系统中也需要安装有ssh功能的程序，例如[plink](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html)。ssh与plink的用法有些地方不一致。目前只支持`ssh`和`plink`。

## 用法

```plain
$ alauda exec -h
usage: alauda service exec [-h] [-c CLIENT] [-n NAMESPACE] [-v]
                           container command [command ...]

Alauda exec

positional arguments:
  container             Container instance name, in the form of <service
                        name>.<container number>, where <container number>
                        defaults to 0 if absent
  command               Command to execute

optional arguments:
  -h, --help            show this help message and exit
  -c CLIENT, --client CLIENT
                        The command name of ssh client, support ssh and plink,
                        in the form of <ssh_client>:<client_path>, where
                        <client_path> defaults to the same as ssh_client if
                        absent. The default is ssh
  -n NAMESPACE, --namespace NAMESPACE
                        Service namespace
  -v, --verbose         show more info
```

以下示例中假定登录用户名为`user01`。

### 示例1
```plain
$ alauda exec -v first ls /
[alauda info] service name: first
[alauda info] namespace: user01
[alauda info] ssh client: ssh
[alauda info] the path of ssh client: ssh
[alauda info] command: ssh -p 4022 -t user01@exec.alauda.cn first ls /
user01@exec.alauda.cn's password:
bin   dev  home  lib64	mnt  proc  run.sh  selinux	   srv	tmp  var
boot  etc  lib	 media	opt  root  sbin    set_root_pw.sh  sys	usr
Connection to exec.alauda.cn closed.
[alauda] OK
```
上面的命令，是在已登录用户`user01`的`first`服务下的容器实例0（默认是容器实例0）中执行命令`ls -l`。
如果是使用当前用户第一次对某服务下的容器实例执行exec，
会在配置文件`~/.alaudacfg`中添加从alauda网络API中抓取的exec_endpoint信息：
```json
{
  "username": "user01",
  "exec_endpoint": {
    "first": "exec.alauda.cn"
  },
  "auth": {
    "token": "**************",
    "endpoint": "https://api.alauda.cn/v1/"
  }
}
```
这样下次可以直接从配置文件中取得`exec_endpoint`信息，而不是再次从网络中抓取。

若未指定ssh客户端，默认为ssh命令。

## 示例2

在未登录的情况下使用exec。

退出当前登录。
```plain
$ alauda logout
[alauda] Bye
[alauda] OK
```

指定命名空间（这里是用户名），使用exec：
```plain
$ alauda exec -v -n user01 first ls /
[alauda info] use default exec endpoint: exec.alauda.cn
[alauda info] namespace: user01
[alauda info] ssh client: ssh
[alauda info] the path of ssh client: ssh
[alauda info] command: ssh -p 4022 -t user01@exec.alauda.cn first ls /
user01@exec.alauda.cn's password:
bin   dev  home  lib64	mnt  proc  run.sh  selinux	   srv	tmp  var
boot  etc  lib	 media	opt  root  sbin    set_root_pw.sh  sys	usr
Connection to exec.alauda.cn closed.
[alauda] OK
```

在未登录的情况下使用`exec`，`exec_endpoint`使用默认值`exec.alauda.cn`。

## 示例3
```plain
$ alauda exec -v -c ssh:/usr/bin/ssh -n user01 first.0 /bin/bash
[alauda info] use default exec endpoint: exec.alauda.cn
[alauda info] namespace: user01
[alauda info] ssh client: ssh
[alauda info] the path of ssh client: /usr/bin/ssh
[alauda info] command: /usr/bin/ssh -p 4022 -t user01@exec.alauda.cn first.0 /bin/bash
user01@exec.alauda.cn's password:
root@0a9351f8ade4:/# ls /
bin   dev  home  lib64	mnt  proc  run.sh  selinux	   srv	tmp  var
boot  etc  lib	 media	opt  root  sbin    set_root_pw.sh  sys	usr
```
`-c ssh:/usr/bin/ssh`是指使用ssh命令，这个命令路径是`/usr/bin/ssh`，这种方法适用于系统PATH中找不到ssh命令这一情况。
`first.0`是指`first`服务下的容器实例0。

如果要使用plink，可以这样做：
```plain
$ alauda exec -v -c plink -n user01 first.0 /bin/bash
```
或者
```plain
$ alauda exec -v -c plink:/path/to/plink -n user01 first.0 /bin/bash
```
