class ItemCounter:
    def __init__(self, class_names, counting_line_x, margin_reset=100, max_salt=200):
        self.class_counting = {nombre: 0 for nombre in class_names}
        self.counting_line_x = counting_line_x
        self.margin_reset = margin_reset
        self.max_salt = max_salt
        
        self.previus_x_center = None
        self.already_counted = False

    def update_and_check(self, centro_x, nombre_clase):
        """Evalúa si la fruta cruzó la línea. Retorna True si acaba de ser contada."""
        is_cut_now = False
        line_distance = abs(centro_x - self.counting_line_x)
        
        if line_distance > self.margin_reset:
            self.already_counted = False

        if self.previus_x_center is not None:
            salt_distance = abs(centro_x - self.previus_x_center)
            
            if salt_distance >= self.max_salt:
                self.already_counted = False
            elif not self.already_counted:
                # Verificar cruce (izquierda a derecha o derecha a izquierda)
                if (self.previus_x_center < self.counting_line_x and centro_x >= self.counting_line_x) or \
                   (self.previus_x_center > self.counting_line_x and centro_x <= self.counting_line_x):
                    
                    self.class_counting[nombre_clase] += 1
                    self.already_counted = True
                    is_cut_now = True

        self.previus_x_center = centro_x
        return is_cut_now

    def reset_tracking(self):
        """Reinicia la memoria de posición (cuando la fruta sale de pantalla)."""
        self.previus_x_center = None