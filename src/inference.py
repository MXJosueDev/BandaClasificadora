import numpy as np
import cv2
from ai_edge_litert.interpreter import Interpreter

class ModelInference:
    def __init__(self, model_path, labels_path):
        with open(labels_path, 'r', encoding='utf-8') as archivo:
            self.class_names = [line.strip() for line in archivo]

        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]
        self.is_floating_model = (self.input_details[0]['dtype'] == np.float32)

    def predict(self, roi_bgr):
        """Recibe una región de interés (ROI), la preprocesa y retorna la predicción."""
        rgb_roi = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
        resized_roi = cv2.resize(rgb_roi, (self.width, self.height))
        input_data = np.expand_dims(resized_roi, axis=0)

        if self.is_floating_model:
            input_data = np.float32(input_data)

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        results = np.squeeze(output_data)

        class_id = np.argmax(results)
        confidence = results[class_id]
        
        return self.class_names[class_id], confidence