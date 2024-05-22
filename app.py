from managers.authentication_manager import AuthenticationManager
from managers.models_manager import ModelSelection

authenticator = AuthenticationManager()
authenticator.start_authentication()

if authenticator.get_user() is not None:
    validator_name = authenticator.get_user()
    models_manager = ModelSelection(validator_name)    
    models_manager.show_window()

