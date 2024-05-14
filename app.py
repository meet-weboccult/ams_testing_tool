from managers.authentication_manager import AuthenticationManager
from managers.models_manager import ModelSelection
from models.mobile_detection import MobileDetection

authenticator = AuthenticationManager()
authenticator.start_authentication()
user = authenticator.get_user()

if user is not None:
    model_manager = ModelSelection()
    model_manager.add_model({"Mobile Detection":MobileDetection})
    selected_model = model_manager.show_window()
    selected_model()
