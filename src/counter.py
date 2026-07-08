class ItemCounter:
    def __init__(self, class_names, linea_conteo_x, margen_reset=100, max_salto=200):
        self.conteo_clases = {nombre: 0 for nombre in class_names}
        self.linea_conteo_x = linea_conteo_x
        self.margen_reset = margen_reset
        self.max_salto = max_salto
        
        self.centro_x_previo = None
        self.ya_contada = False

    def update_and_check(self, centro_x, nombre_clase):
        """Evalúa si la fruta cruzó la línea. Retorna True si acaba de ser contada."""
        fue_contada_ahora = False
        distancia_a_linea = abs(centro_x - self.linea_conteo_x)
        
        if distancia_a_linea > self.margen_reset:
            self.ya_contada = False

        if self.centro_x_previo is not None:
            distancia_salto = abs(centro_x - self.centro_x_previo)
            
            if distancia_salto >= self.max_salto:
                self.ya_contada = False
            elif not self.ya_contada:
                # Verificar cruce (izquierda a derecha o derecha a izquierda)
                if (self.centro_x_previo < self.linea_conteo_x and centro_x >= self.linea_conteo_x) or \
                   (self.centro_x_previo > self.linea_conteo_x and centro_x <= self.linea_conteo_x):
                    
                    self.conteo_clases[nombre_clase] += 1
                    self.ya_contada = True
                    fue_contada_ahora = True

        self.centro_x_previo = centro_x
        return fue_contada_ahora

    def reset_tracking(self):
        """Reinicia la memoria de posición (cuando la fruta sale de pantalla)."""
        self.centro_x_previo = None