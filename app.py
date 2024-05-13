from authentication_manager import AuthenticationManager
from models_manager import ModelSelection
from models.mobile_detection import MobileDetection

# authenticator = AuthenticationManager()
# result = authenticator.start_authentication()

model_manager = ModelSelection()
model_manager.add_model({"Mobile Detection":MobileDetection})
model_manager.show_window()
