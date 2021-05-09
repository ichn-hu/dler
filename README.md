
# Usage

You need python3 in order to execute the script.

Use `python3 script.py --help` to print the help message.

Example usage.

## Parse the subscription

You need to register on the service provider, use [register link](https://dler.best/auth/register?affid=64191) to register.

And you will get a `$subscribe_token`, something like `DJNVz40XPswqYnrz`.

Use

```
python3 script.py -t DJNVz40XPswqYnrz
```

And you will note that connection scripts will be created inside `ss/`.

## Connect

You can walk into `ss/` and `./XXX.sh -l 1080 -v` to connect. `XXX` is the script name, `-l 1080` let the client expose the proxy at port 1080, `-v` prints a verbose log for debugging purpose.

You can also use `script.py` to connect. You need to provide prefix of the connection script and it will random pick one among those scripts that matched the prefix. Say if you want to connect to the USA, just type

```
python3 script.py -t DJNVz40XPswqYnrz -c US
```

If you want to connect to TW BGP, you can

```
python3 script.py -t DJNVz40XPswqYnrz -c TW-BGP
```

# More on tools

You need to have `ss-local` and `simple-obfs` installed in order to execute the script.

Or you can use the Dockerfile.

## ss to http

Many shell only supports HTTP proxy, you might need to convert ss to HTTP. Try `polipo` or `privoxy`.

For `polipo`:

```
yay -S polipo
sudo systemctl enable polipo
sudo systemctl start polipo

# modify /etc/polipo/config
socksParentProxy = "localhost:1080"
socksProxyType = socks5
```

Add the following line in `/etc/profile` to allow global proxy, where `8123` is the default HTTP proxy port of `polipo`.

```
export http_proxy="http://127.0.0.1:8123"
export https_proxy="http://127.0.0.1:8123"
```

For single command, try `proxychains-ng`

```
yay -S proxychains-ng
sudo vim /etc/proxychains.conf

# modify the last line
socks5  127.0.0.1 1080
```

Prepend `porxychains -q` to a shell command to proxy the traffic, say

```
proxychains -q git fetch
```

## test the proxy

```
curl ipinfo.io
proxychains -q curl ipinfo.io
```

or

```
curl ip.sb
proxychains -q curl ip.sb
```

If the result between the two command changed, it means the proxy is working.
