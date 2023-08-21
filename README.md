# Recipie

Python idoms and recipes

# Submodule

Some recipie modules having the same name with standard libraries are meant
as a drop in replacement for their counter parts. For example:

```
# Replace contextlib by recipie.contextlib

#from contextlib import *
from recipie.contextlib import *

# All standard contextlib and recipie.contextlib extensions are available
```

## contextlib

### commit(func, *args, **kwargs) [0.0.1]

Executes *func* if the code ran to completion without any error:

Example:

```
def save_data(data):
    ...

with commit(save_data, data):
    # other actions
    ...

    # save_data is called if there is no error
```

* Also see ***rollback***

### rollback(func, *args, **kwargs) [0.0.1]

Executes *func* if when encouter error

Example:

```
def undo(data):
    ...

with rollback(undo, data):
    # Other actions
    ...
```

* Also see ***commit

### Buffer
Accumulates data into a buffer to be processed when the buffer is full.

Example:

```
def save_data(data: list[int]):
    ...

with Buffer(1000, save_data) as buffer:
    for i in range(1500):
        buffer.add(i) # On 1001th item, called save_data to save previous 1000 items
# When out of context, call save_data on the last 500 items
```

## functools

### @scoped

*"Namespaces are one honking great idea -- let's do more of those!"*


Decorates a function to make it part of another namespace


Examples:
'''
def retry():
    ...

# retry.no_delay
@scoped(retry)
def no_delay():
    ...
'''

### @default_on_error(value, errors) [0.0.1]

Decorates a function to return the specified *value* if *errors* is raised.

*value*: Default value to return on error

*errors*: Error or tuple of errors to check for

Example:

```
@default_on_error(None, KeyError)
def get_from_dict(dict_, key):
    return dict_[key] # Possible KeyError

value = get_from_dict(d, "Test") # Value is None when "Test" is not in d

```

### @skip_on_error(errors) [0.0.1]

Decorates a function to return None if *errors* is raised (equivalent to @default_on_error(None, errors)

### @retry(tries, errors, error_filter, delay_gen, log_error) [0.0.1]

Retries function *tries* times if encounter an error that matches errors and error_filter

*tries*: Number of attempts on the function. Must be at least 2

*errors*: exception or tuple of exception to retry

*error_filter*: function that takes in an error and returns
**True** if it is a retriable error

*delay_gen*: Delay generator that produce an iterator of delay values for
use between attempts. Several predefined delay scheme:

* retry.no_delay (default): No delay between calls (equivalent to retry.const_delay(0)).
* retry.const_delay(5): Delay five seconds every time (Delay values are [5, 5, 5, 5, ...]
* retry.exp_delay(5, 100): Delays values are [5, 10, 20, 40, ... 5 * 2 ^ (n - 1)]

Example:

```
@retry(3, NetworkError) # Retry 3 times on NetworkError)
def get_db_connection():
   ...

conn = get_db_connection() # Automatically retry on network error
```

* Either *errors* or *error_filter* must be specified
