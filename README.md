# market-back

### How to generate original model file from database

```shell script
python -m pwiz -e mysql -H DB_HOST -p DB_PORT -u DB_USER -P DB_NAME > orig_db.py
```

### Update .env file

```
# env file
USE_CONFIG = "development"

# development environment
DEV_DB_USER = ""
DEV_DB_PASSWORD = ""
DEV_DB_HOST = ""
DEV_DB_PORT = 3306
DEV_DB_NAME = ""
DEV_DB_CHARSET = "utf8"
DEV_API_URL = ""

# production environment
PROD_DB_USER = ""
PROD_DB_PASSWORD = ""
PROD_DB_HOST = ""
PROD_DB_PORT = 3306
PROD_DB_NAME = ""
PROD_DB_CHARSET = "utf8"
PROD_API_URL = ""
```