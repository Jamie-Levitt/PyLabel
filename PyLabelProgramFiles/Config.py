import os, json

if os.sep == '\\':
    configPath = ('C:\Program Files\PyLabel\config.json')
elif os.sep == '/':
    configPath = '/usr/local/PyLabel/config.json'

def loadConfig() -> dict:
    if os.path.isfile(configPath) is False:
        os.chdir('C:\Program Files\PyLabel')
        with open('config.json', 'w') as file:
            config = {
                'printer-model': "QL-820NWB",
                'printer-ip': "192.168.0.51"
            }
            json.dump(config, file)
            file.close()
    configFile = open(configPath)
    configData = json.load(configFile)

    config = {
                'printer-model': configData['printer-model'],
                'printer-ip': configData['printer-ip']
    }

    configFile.close()
    return config

def getConfigSetting(setting:str) -> str:
    config = loadConfig()
    return config[setting]

def setConfigSetting(setting:str, value:str):
    config = loadConfig()
    config[setting] = value

    with open(configPath, 'w') as configFile:
        json.dump(config, configFile)