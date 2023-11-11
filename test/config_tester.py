# main.py
from config.config_single import CONFIG_KEY1, CONFIG_KEY2

print("Config Key 1:", CONFIG_KEY1)
print("Config Key 2:", CONFIG_KEY2)


# main.py
from config.config_nested import CONFIG

# Accessing nested configuration values
print("Config Key 1:", CONFIG['section1']['key1'])
print("Database Host:", CONFIG['database']['host'])

