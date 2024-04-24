import os
from pydantic_settings import BaseSettings


class SettingsForMongo(BaseSettings):
    # DB Settings
    # MONGO_PRIVATE_URL: str = str(os.environ.get("MONGO_PRIVATE_URL"))
    MONGOHOST:str = os.environ.get("MONGOHOST")
    MONGOPASSWORD:str = os.environ.get("MONGOPASSWORD")
    MONGOPORT:int = os.environ.get("MONGOPORT")
    MONGOUSER:str = os.environ.get("MONGOUSER")


    # class Config:
    #     env_file = ".env"

    @property
    def MONGOHOST(self):
        host = f"{self.MONGOHOST}"
        return host
    
    
    @property
    def MONGOPASSWORD(self):
        password = f"{self.MONGOPASSWORD}"
        return password
    
    
    @property
    def MONGOPORT(self):
        port = int(self.MONGOPORT)
        return port
    
    
    @property
    def MONGOUSER(self):
        user = f"{self.MONGOUSER}"
        return user


settings_for_mongo = SettingsForMongo()