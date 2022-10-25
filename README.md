# dotenv

Examples

```py
import dotenv
import os

dotenv.load_dotenv()
EXAMPLE = os.getenv("LOADED_EXAMPLE")
```

```py
import dotenv

dotenv.load_dotenv()
EXAMPLE = dotenv.getenv("LOADED_EXAMPLE", cast=int) # Will pass the value through the cast function
```

```py
# set key

import dotenv

dotenv.load_dotenv()
dotenv.set_key("SET_EXAMPLE", 5, override_env=True) # override_env indicates whether it should override any existing key with the same name
EXAMPLE = dotenv.getenv("SET_EXAMPLE", cast=int)
```

```py
# remove key

import dotenv

dotenv.load_dotenv()
dotenv.remove_key("SET_EXAMPLE", override_env=True) # override_env will remove the key from the environ
dotenv.getenv("SET_EXAMPLE") # The value will be None
```
