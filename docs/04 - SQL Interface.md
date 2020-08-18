# SQL Interface

This is what we use to store our config data.
You can import the module from __config.py__ like this:

``` python
from config import Config

# (As an example) Declare it first in main.py
Config.set_init('a-config', 'a-value')

# You can then set/get it whichever file want
curr_val = Config.get('a-config')
Config.set('a-config', curr_val * 2)
```

## Command list

Commands are:

- `Config.set_init(name, value)`
    * Sets the `name` to `value` if `name` doesn't exist in DB
- `Config.set(name, value)`
    * Sets the `name` to `value` regardless
- `Config.get(name)`
    * Gets the `name`, returns `None` if `name` doesn't exist in DB
- `Config.channels()`
    * Returns all configs ending with `-channel` suffix


__Warning__: Use `set_init` in main.py to keep a track of what configs we utilize. Do not use `set` directly without first declaring the config with `set_init`.


> Next, read the [roadmap](05%20-%20Roadmap.md)