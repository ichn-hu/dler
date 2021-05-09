使用方法：

```
python dler-ss.py -s https://dler.cloud/subscribe/XXXXXXXX\?mu\=ss
chmod +x *.sh
./xxx.sh -v -l 1080
```

中间 `XXXX` 替换成 subscription token。其中 `-l` 指定的是本地的 sock5 监听端口。

推荐使用 `polipo` 把 socks 转换成 http 代理，这样可以提供给 shell 使用。

```
yay -S polipo
sudo systemctl enable polipo
sudo systemctl start polipo

# 修改 /etc/polipo/config
socksParentProxy = "localhost:1080"
socksProxyType = socks5
```

全局翻墙可以在 `/etc/profile` 中指定，其中 `8123` 是 polipo 的默认转换端口。

```
export http_proxy="http://127.0.0.1:8123"
export https_proxy="http://127.0.0.1:8123"
```

如果不想使用全局翻墙，可以安装 `proxychains-ng`，然后配置下

```
yay -S proxychains-ng
sudo vim /etc/proxychains.conf
# 修改配置如下
socks5  127.0.0.1 1080
```

然后在执行的命令前使用 `porxychains -q` 则可以强制让命令网络流量走代理，如

```
proxychains -q git fetch
```

嘻嘻~

附加一个如何检查网络状态的方式~

```
curl ipinfo.io
proxychains -q curl ipinfo.io
```
