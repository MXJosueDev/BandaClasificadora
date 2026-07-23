class ItemCounter:
    def __init__(self, class_names, counting_line, orientation="vertical", margin_reset=100, max_salt=200):
        self.class_counting = {nombre: 0 for nombre in class_names}
        self.counting_line = counting_line
        self.orientation = orientation
        self.margin_reset = margin_reset
        self.max_salt = max_salt
        
        self.previus_axis_center = None
        self.already_counted = False

    def update_and_check(self, center_x, center_y, class_name):
        """Evalúa si la fruta cruzó la línea. Retorna True si acaba de ser contada."""
        is_cut_now = False
        axis_center = center_x if self.orientation == "vertical" else center_y
        line_distance = abs(axis_center - self.counting_line)
        
        if line_distance > self.margin_reset:
            self.already_counted = False

        if self.previus_axis_center is not None:
            salt_distance = abs(axis_center - self.previus_axis_center)
            
            if salt_distance >= self.max_salt:
                self.already_counted = False
            elif not self.already_counted:
                # Verificar cruce según la orientación elegida.
                if (self.previus_axis_center < self.counting_line and axis_center >= self.counting_line) or \
                   (self.previus_axis_center > self.counting_line and axis_center <= self.counting_line):
                    
                    self.class_counting[class_name] += 1
                    self.already_counted = True
                    is_cut_now = True

        self.previus_axis_center = axis_center
        return is_cut_now

    def reset_tracking(self):
        """Reinicia la memoria de posición (cuando la fruta sale de pantalla)."""
        self.previus_axis_center = None