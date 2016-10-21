# Flash

Increase your download speeds by downloading from multiple IP addresses simultaneously!

You can either have multiple IP addresses on the same adapter or have multiple network adapters.
If you want to use a subset of your IP addresses, change [`get_ip_addresses`](https://github.com/avamsi/Flash/blob/master/utils.py#L5) function in [`utils.py`](https://github.com/avamsi/Flash/blob/master/utils.py)

## Usage
Install `requests` and `requests_toolbelt`
```
pip3 install requests
pip3 install requests_toolbelt
```

Run [`flash.py`](https://github.com/avamsi/Flash/blob/master/flash.py) and enter download url(s) as input for the script (I know, I know, I should change that)
```
python3 flash.py
```

---

**NOTE:** <del>Flash is supposed to be cross-platform but [`utils.py`](https://github.com/avamsi/Flash/blob/master/utils.py) is Windows only.</del>  
Flash is now cross-platfrom (contributed by [@j3rw1N](https://github.com/j3rw1N) in [#2](https://github.com/avamsi/Flash/pull/2)). Feel free to contribute!
