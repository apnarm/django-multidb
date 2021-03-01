# Django multidb
## Overview
This module is largely a refactoring and port of the original 
[django-readwrite](https://github.com/apnarm/django-readwrite) module, bring it into contemporary python and django 
versions.

---
**NOTE**
Status: this is a work in progress and is probably not usable (yet).
---

### From the original README (with edits)
Read/write database splitting for Django, based on the HTTP request method.

### Addenum
Tested against Django 3.1

#### Features:
* Makes Django use a configured database for an entire
  HTTP request according to configured HTTP methods
  (GET, POST, etc) and URL paths.
* Chooses a random connection if there are multiple
  databases configured for a request - poor man's
  database load balancing.
* Raises an error if a view tries to write to a
  read-only database.
* No issues with database replica latency,
  and reading data before it has been synchronized.
* No need to specify any database with `using=`
  in all of your model/transaction code.
* No need to set up database routers.
* Database transactions work as expectd;
  reads won't read from a different transaction
  to the writes.
* Read-only command to force all requests to use a
  read-only database connection.

Extras:
* `@pre_commit` and `@post_commit` function decorators.

## Usage

1. Install `django-multidb` module as usual (pip, pipenv)

2. Add `multidb` to the top of your `INSTALLED_APPS` setting.

3. Replaces TransactionMiddleware in `MIDDLEWARE` with:
    * `multidb.middleware.MultiDBMiddleware`
    * `multidb.middleware.ReadOnlyMiddleware`
    * `multidb.middleware.MultiDBTransactionMiddleware`

4. Update your database settings to include:
    * HTTP_PATHS
    * HTTP_METHODS
    * READ_ONLY or READ_ONLY_WARNING

Example:
```
    DATABASES = {
        'default': {
            'ENGINE': engine,
            'HOST': primary_host,
            'PORT': primary_port,
            'NAME': primary_database,
            'USER': primary_user,
            'PASSWORD': primary_password,

            # Set HTTP_PATHS to force request paths to use a database.
            # This ensures that the admin always uses the primary database.
            'HTTP_PATHS': ['/admin/'],

        },
        'readonly1': {
            'ENGINE': engine,
            'HOST': replica1_host,
            'PORT': replica1_post,
            'NAME': replica1_name,
            'USER': replica1_user,
            'PASSWORD': replica1_password,

            # Set HTTP_METHODS to force request methods to use a database.
            # This ensures that GET and HEAD requests use the read-only replica.
            # Adding None to the list means that it will also be used outside
            # of requests (e.g. if your application access the database during
            # process initialization).
            'HTTP_METHODS': ('GET', 'HEAD', None),

            # Set READ_ONLY to disable write SQL queries on a database.
            'READ_ONLY': True,

            # Enable autocommit avoid creating transactions
            # on databases which will never have writes.
            'OPTIONS': {
                'autocommit': True,
            }
        }
        'readonly2': {...}
    }
```
