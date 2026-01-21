class AppSettings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppSettings, cls).__new__(cls)
            cls._instance.timezone = "UTC" # Valor por defecto
        return cls._instance

    def set_timezone(self, tz: str):
        self.timezone = tz

    def get_timezone(self):
        return self.timezone

# Instancia global (Singleton)
settings = AppSettings()