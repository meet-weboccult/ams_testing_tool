from mobile_detection import MobileDetection
from managers.authentication_manager import AuthenticationManager
from managers.models_manager import ModelSelection

authenticator = AuthenticationManager()
authenticator.start_authentication()

if authenticator.get_user() is not None:
    models_manager = ModelSelection()
    models_manager.add_model({"Mobile Detection":MobileDetection})
    model = models_manager.show_window()
    
    model()
