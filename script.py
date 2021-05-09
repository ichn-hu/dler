import re
import os
import base64
import logging
import argparse
import random
from collections import defaultdict
import urllib.parse, urllib.request

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

SUB_LINK_TEMPLATE = "https://dler.cloud/subscribe/{}?mu=ss"
SS_SCHEMA = 'ss://'
REGION_CONFIG = [
    ('美国', 'US'),
    ("俄罗斯", "RU"),
    ("印度", "IN"),
    ("日本", "JA"),
    ("中国", "CN"),
    ("德国", "DE"),
    ("台湾", "TW"),
    ("新加坡", "SG"),
    ("澳大利亚", "AU"),
    ("香港", "HK"),
    ("菲律宾", "PH"),
    ("英国", "UK"),
    ("土耳其", "TU"),
    ("韩国", "KO"),
    ("爱尔兰", "IR"),
    ("巴西", "BR"),
]

collection = defaultdict(list)

def decode(s):
    s += '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s).decode()

def parse_ss(ss_link):
    config = {
        "server":"",
        "server_port":0,
        "password":"",
        "method":"",
        "plugin":"",
        "plugin-opts":"",
        "name":"",
        "group":"",
    }
    if ss_link.startswith(SS_SCHEMA):
        info = ss_link[len(SS_SCHEMA):]

        if info.rfind("#") > 0:
            info, _ps = info.rsplit("#", 1)
            name = urllib.parse.unquote(_ps)
            region = ''
            for region in REGION_CONFIG:
                if name.startswith(region[0]):
                    name = name.replace(region[0], region[1])
                    name = name.replace(" ", "-")
                    collection[region[0]].append(name)
                    break

            config["name"] = name

        if info.rfind("/?") > 0:
            info, _opts = info.split("/?", 1)
            opts = _opts.split("&")
            group = "group="
            plugin = "plugin="
            for opt in opts:
                if opt.startswith(group):
                    config["group"] = decode(opt[len(group):])
                if opt.startswith(plugin):
                    config["plugin"], config["plugin-opts"] = urllib.parse.unquote(opt[len(plugin):]).split(";", 1)

        if info.find("@") < 0:
            # old style link
            #paddings
            blen = len(info)
            if blen % 4 > 0:
                info += "=" * (4 - blen % 4)

            info = base64.b64decode(info).decode()

            atidx = info.rfind("@")
            method, password = info[:atidx].split(":", 2)
            addr, port = info[atidx+1:].split(":", 2)
        else:
            atidx = info.rfind("@")
            addr, port = info[atidx+1:].split(":", 1)

            info = decode(info[:atidx])
            method, password = info.split(":", 1)

        config["server"] = addr
        config["server_port"] = port
        config["method"] = method
        config["password"] = password
    return config

SCRIPT_TEMPLATE = """
#!/bin/bash
echo "connectting {group} - {name}"
ss-local -s {server} -p {server_port} -k {password} -m {method} {options} {additions}
"""

def make_script(config):
    if config["plugin"] != "":
        config["options"] = '--plugin %s --plugin-opts "%s"' % (config["plugin"], config["plugin-opts"])
    else:
        config["options"] = ""
    if "additions" not in config or config["additions"] == "":
        # keep the parameters from calling this script and pass them to ss-local
        config["additions"] = '"$@"'
    return SCRIPT_TEMPLATE.format(**config)

def read_subscribe(sub_url):
    logging.info("reading from subscribe ...")
    sub_text = ""
    if os.path.exists(sub_url):
        sub_text = open(sub_url, "rb").read()
    else:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = urllib.request.Request(url=sub_url,headers=headers)
        with urllib.request.urlopen(req) as response:
            sub_text = response.read()
    logging.info("read %d byte from %s", len(sub_text), sub_url)

    return base64.b64decode(sub_text + b'=' * (-len(sub_text) % 4)).decode().splitlines()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dler parses the subscription into ss scripts")
    parser.add_argument('-t', '--token', action="store", default="", required=False, help="subscribe_token, used in {}".format(SUB_LINK_TEMPLATE.format("$subscribe_token")))
    parser.add_argument('-s', '--subscribe',
                        action="store",
                        default="",
                        required=False,
                        help="read from a subscribe url or a local file")
    parser.add_argument('-d', '--dir', default='ss', help="directory to place the connections")
    parser.add_argument('-c', '--connect', default='', help='execute a connection script given the name. if the provided name matches the prefix of multiple files, it will randomly pick one.')
    parser.add_argument('-p', '--port', default=1080, help='port to use when connect')
    option = parser.parse_args()

    if option.subscribe != "" or option.token != "":
        sub_link = option.subscribe
        if option.token != "":
            sub_link = SUB_LINK_TEMPLATE.format(option.token)
        logging.info("read subscription from %s", sub_link)
        ss_links = read_subscribe(sub_link)
        logging.info("read total %d connections", len(ss_links))
        os.makedirs(option.dir, exist_ok=True)
        for link in ss_links:
            config = parse_ss(link)
            file_path = os.path.join(option.dir, config["name"] + '.sh')
            open(file_path, "w").write(make_script(config))
            os.chmod(file_path, 0o775)
        logging.info("write %d different region connection to disk", len(collection))
        for k, v in collection.items():
            logging.info("region %s(%d): %s", k, len(v), ", ".join(v))
    
    if option.connect != "":
        scripts = [f for f in os.listdir(option.dir) if f.startswith(option.connect)]
        logging.info('found %d matched script', len(scripts))
        pick = random.choice(scripts)
        logging.info('pick %s, connect using port %d', pick, option.port)
        os.system('%s -v -l %d' % (os.path.join(option.dir, pick), option.port))
    
