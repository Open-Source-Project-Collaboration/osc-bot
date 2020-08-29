# SQL Interface

This is what we use to store our data. Please check [the tables](10%20-%20Tables.md) to see which data we store.

_**Example**: You can import the module from __config.py__ like this:_

``` python
from config import Config

# (As an example) Declare it first in main.py
Config.set_init('a-config', 'a-value')

# You can then set/get it whichever file want
curr_val = Config.get('a-config')
Config.set('a-config', curr_val * 2)
```

## Modules
Please check [the tables](10%20-%20Tables.md) for information about different modules and their methods.


> Next, read the [roadmap](05%20-%20Roadmap.md)