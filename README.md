Tornado Binary MemCache
=======================

This library provides a simple interface for asynchronously accessing MemCache using it's Binary protocol.
The binary protocol permits compression to be used (using zlib) for large values.

The only implemented methods are **get** and **set**!

This library was **not** extensively tested, so it might still contain some bugs.<br />
**USE AT YOUR OWN RISK!!**

### Features

* Asynchronous (Tornado)
* Binary protocol
* Supports compression using zlib
* Connection pool with hashed key distribution between servers. The hash function may be user-defined, if needed
* CAS get/set support

### TODOs

* Probably better error handing
* ~~Auto-close long-idle unused connections~~

### Requirements

* Tornado >= 3.2

### How to install

```
git clone https://github.com/terra/tornadobmc.git
cd tornadobmc
python setup.py install
```

### Example usage

An example usage is given in the _test.py_ file.
