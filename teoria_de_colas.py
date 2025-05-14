import math

class QueueTheoryCalculator:
    def __init__(self):
        self.lambda_ = 0  # Tasa de llegada
        self.mu = 0       # Tasa de servicio
        self.k = 1        # Número de servidores
        self.M = 0        # Población (para modelos finitos)
        self.n = 0        # Número de clientes para Pn
        self.op = 0       # Modelo seleccionado (1: PICS, 2: PICM, 3: PFCS, 4: PFCM)
        
        # Costos
        self.costo_unitario = 0
        self.horas_laborables = 8  # Valor por defecto
        self.costo_diario = 0

    def set_parameters(self, lambda_, mu, k=1, M=0, n=0, op=1):
        """Establece los parámetros del modelo"""
        self.lambda_ = lambda_
        self.mu = mu
        self.k = k
        self.M = M
        self.n = n
        self.op = op

    def set_cost_parameters(self, costo_unitario, costo_diario, horas_laborables=8):
        """Establece los parámetros de costos"""
        self.costo_unitario = costo_unitario
        self.costo_diario = costo_diario
        self.horas_laborables = horas_laborables

    # --------------------- CÁLCULOS BÁSICOS ---------------------
    
    def calcular_factorial(self, n):
        """Calcula el factorial de un número"""
        return math.factorial(n) if n >= 0 else 1
    
    def es_estable(self): #condicion de estabilidad
        """Verifica la estabilidad del sistema"""
        if self.op == 1:
            return self.lambda_ / self.mu < 1

    def calcular_ro(self): # p
        """Calcula ρ (ro) - Factor de utilización del sistema (λ/μ)"""
        if self.op == 1:  # PICS
            return self.lambda_ / self.mu
        elif self.op == 2:  # PICM
            return self.lambda_ / (self.k * self.mu)
        else:
            return 0  # No aplica para otros modelos
        

    def calcular_P0(self):
        """Calcula P0 - Probabilidad de que no haya clientes en el sistema"""
        
        if self.op == 1:  # M/M/1 (PICS)
            if self.es_estable():
                return 1 - self.calcular_ro()
            else:
                raise ValueError("El sistema no es estable. La tasa de llegada entre la tasa de servicio debe ser menor que 1.")   
        
        elif self.op == 2:  # M/M/k (PICM)
            sumatoria = 0
            for n in range(self.k):
                term = (1 / self.calcular_factorial(n)) * ((self.lambda_ / self.mu) ** n)
                sumatoria += term
            
            ultimo_term = (1 / self.calcular_factorial(self.k)) * ((self.lambda_ / self.mu) ** self.k)
            denom = (self.k * self.mu) / (self.k * self.mu - self.lambda_)
            
            return 1 / (sumatoria + ultimo_term * denom)
        
        elif self.op == 3:  # M/M/1/M/M (PFCS)
            sumatoria = 0
            for n in range(self.M + 1):
                term = (self.calcular_factorial(self.M) / 
                       self.calcular_factorial(self.M - n)) * ((self.lambda_ / self.mu) ** n)
                sumatoria += term
            return 1 / sumatoria
        
        elif self.op == 4:  # M/M/k/M/M (PFCM)
            sumatoria1 = 0
            for n in range(self.k):
                term = (self.calcular_factorial(self.M) / 
                       (self.calcular_factorial(self.M - n) * self.calcular_factorial(n))) * ((self.lambda_ / self.mu) ** n)
                sumatoria1 += term
            
            sumatoria2 = 0
            for n in range(self.k, self.M + 1):
                term = (self.calcular_factorial(self.M) / 
                       (self.calcular_factorial(self.M - n) * self.calcular_factorial(self.k) * (self.k ** (n - self.k)))) * ((self.lambda_ / self.mu) ** n)
                sumatoria2 += term
            
            return 1 / (sumatoria1 + sumatoria2)
        
        return 0

    def calcular_Pn(self, n=None):
        """Calcula Pn - Probabilidad de que haya n clientes en el sistema"""
        if n is None:
            n = self.n
        
        if self.op == 1:  # M/M/1 (PICS)
            if self.es_estable():
                return self.calcular_P0() * (self.calcular_ro() ** n)
            else:
                raise ValueError("El sistema no es estable. La tasa de llegada entre la tasa de servicio debe ser menor que 1.")
        
        elif self.op == 2:  # M/M/k (PICM)
            if n <= self.k:
                return (self.calcular_P0() / self.calcular_factorial(n)) * ((self.lambda_ / self.mu) ** n)
            else:
                return (self.calcular_P0() / (self.calcular_factorial(self.k) * (self.k ** (n - self.k)))) * ((self.lambda_ / self.mu) ** n)
        
        elif self.op == 3:  # M/M/1/M/M (PFCS)
            return (self.calcular_factorial(self.M) / 
                   self.calcular_factorial(self.M - n)) * ((self.lambda_ / self.mu) ** n) * self.calcular_P0()
        
        elif self.op == 4:  # M/M/k/M/M (PFCM)
            if 0 <= n <= self.k:
                return (self.calcular_P0() * (self.calcular_factorial(self.M) / 
                       (self.calcular_factorial(self.M - n) * self.calcular_factorial(n))) * ((self.lambda_ / self.mu) ** n))
            else:
                return (self.calcular_P0() * (self.calcular_factorial(self.M) / 
                       (self.calcular_factorial(self.M - n) * self.calcular_factorial(self.k) * (self.k ** (n - self.k))))) * ((self.lambda_ / self.mu) ** n)
        
        return 0

    def calcular_Pk(self):
        """Calcula Pk - Probabilidad de que todos los servidores estén ocupados (PICM)"""
        if self.op != 2:
            return 0
        
        return ((1 / self.calcular_factorial(self.k)) * ((self.lambda_ / self.mu) ** self.k) * 
               ((self.k * self.mu) / (self.k * self.mu - self.lambda_)) * self.calcular_P0())

    def calcular_PE(self):
        """Calcula PE - Probabilidad de que un cliente tenga que esperar"""
        if self.op == 3:  # PFCS
            return 1 - self.calcular_P0()
        elif self.op == 4:  # PFCM
            sumatoria = 0
            for n in range(self.k):
                sumatoria += self.calcular_Pn(n)
            return 1 - sumatoria
        return 0

    def calcular_PNE(self):
        """Calcula PNE - Probabilidad de que un cliente no tenga que esperar (PFCM)"""
        return 1 - self.calcular_PE()

    # --------------------- MEDIDAS DE DESEMPEÑO ---------------------

    def calcular_L(self):
        """Número esperado de clientes en el sistema"""
        if self.op == 1:  # M/M/1 (PICS)
            if self.es_estable():
                return self.lambda_ / (self.mu - self.lambda_)
            else:
                raise ValueError("El sistema no es estable. La tasa de llegada entre la tasa de servicio debe ser menor que 1.")
        
        elif self.op == 2:  # M/M/k (PICM)
            term1 = (self.lambda_ * self.mu * ((self.lambda_ / self.mu) ** self.k)) / (self.calcular_factorial(self.k - 1) * ((self.k * self.mu - self.lambda_) ** 2))
            return term1 * self.calcular_P0() + (self.lambda_ / self.mu)
        
        elif self.op == 3:  # PFCS
            return self.M - (self.mu / self.lambda_) * (1 - self.calcular_P0())
        
        elif self.op == 4:  # PFCM
            sumatoria1 = 0
            sumatoria3 = 0
            for n in range(self.k):
                sumatoria1 += n * self.calcular_Pn(n)
                sumatoria3 += self.calcular_Pn(n)
            
            sumatoria3 = self.k * (1 - sumatoria3)
            return sumatoria1 + self.calcular_Lq() + sumatoria3
        
        return 0

    def calcular_Lq(self):
        """Número esperado de clientes en la cola"""
        if self.op == 1:  # M/M/1 (PICS)
            if self.es_estable():
                return (self.lambda_ ** 2) / (self.mu * (self.mu - self.lambda_))
            else:
                raise ValueError("El sistema no es estable. La tasa de llegada entre la tasa de servicio debe ser menor que 1.")
        
        elif self.op == 2:  # M/M/k (PICM)
            term = (self.lambda_ * self.mu * ((self.lambda_ / self.mu) ** self.k)) / (self.calcular_factorial(self.k - 1) * ((self.k * self.mu - self.lambda_) ** 2))
            return term * self.calcular_P0()
        
        elif self.op == 3:  # PFCS
            return self.M - ((self.lambda_ + self.mu) / self.lambda_) * (1 - self.calcular_P0())
        
        elif self.op == 4:  # PFCM
            sumatoria = 0
            for n in range(self.k, self.M + 1):
                sumatoria += (n - self.k) * self.calcular_Pn(n)
            return sumatoria
        
        return 0

    def calcular_Ln(self):
        """Número esperado de clientes en la cola (no vacía)"""
        if self.op == 1:  # M/M/1 (PICS)
            if self.es_estable():
                return self.calcular_L()
            else:
                raise ValueError("El sistema no es estable. La tasa de llegada entre la tasa de servicio debe ser menor que 1.")
        
        elif self.op == 2:  # M/M/k (PICM)
            return self.calcular_Lq() / self.calcular_Pk()
        
        elif self.op in [3, 4]:  # PFCS o PFCM
            return self.calcular_Lq() / self.calcular_PE()
        
        return 0

    def calcular_W(self):
        """Tiempo promedio esperado en el sistema por los clientes"""
        if self.op == 1:  # M/M/1 (PICS)
            if self.es_estable():
                return 1 / (self.mu - self.lambda_)
            else:
                raise ValueError("El sistema no es estable. La tasa de llegada entre la tasa de servicio debe ser menor que 1.")
        
        elif self.op == 2:  # M/M/k (PICM)
            return self.calcular_Wq() + (1 / self.mu)
        
        elif self.op == 3:  # PFCS
            return self.calcular_Wq() + (1 / self.mu)
        
        elif self.op == 4:  # PFCM
            return self.calcular_Wq() + (1 / self.mu)
        
        return 0

    def calcular_Wq(self):
        """Tiempo esperado en la cola por los clientes """
        if self.op == 1:  # M/M/1 (PICS)
            if self.es_estable():
                return self.lambda_ / (self.mu * (self.mu - self.lambda_))
            else:
                raise ValueError("El sistema no es estable. La tasa de llegada entre la tasa de servicio debe ser menor que 1.")
        
        elif self.op == 2:  # M/M/k (PICM)
            term = (self.mu * ((self.lambda_ / self.mu) ** self.k) * self.calcular_P0()) / (self.calcular_factorial(self.k - 1) * ((self.k * self.mu - self.lambda_) ** 2))
            return term
        
        elif self.op == 3:  # PFCS
            return self.calcular_Lq() / ((self.M - self.calcular_L()) * self.lambda_)
        
        elif self.op == 4:  # PFCM
            return self.calcular_Lq() / ((self.M - self.calcular_L()) * self.lambda_)
        
        return 0

    def calcular_Wn(self):
        """Tiempo esperado en la cola para colas no vacías por los clientes"""
        if self.op == 1:  # M/M/1 (PICS)
            if self.es_estable():
                return self.calcular_W()
            else:
                raise ValueError("El sistema no es estable. La tasa de llegada entre la tasa de servicio debe ser menor que 1.")
        
        elif self.op == 2:  # M/M/k (PICM)
            return self.calcular_Wq() / self.calcular_Pk()
        
        elif self.op in [3, 4]:  # PFCS o PFCM
            return self.calcular_Wq() / self.calcular_PE()
        
        return 0

    # --------------------- CÁLCULOS DE COSTOS ---------------------

    def calcular_CTte(self):
        """Costo total de tiempo de espera"""
        return self.lambda_ * self.horas_laborables * self.calcular_Wq() * self.costo_unitario

    def calcular_CTts(self):
        """Costo total de tiempo en el sistema"""
        return self.lambda_ * self.horas_laborables * self.calcular_W() * self.costo_unitario

    def calcular_CTse(self):
        """Costo total de servicio"""
        return self.lambda_ * self.horas_laborables * (1 / self.mu) * self.costo_unitario

    def calcular_CTs(self):
        """Costo total de servidores"""
        return self.k * self.costo_diario

    def calcular_CT(self):
        """Costo total del sistema"""
        return self.calcular_CTts() + self.calcular_CTs()
    
    # --------------------- CÁLCULOS GENERALES ---------------------
    def calculate(self, n=None):
        """
        Calcula todas las medidas de desempeño relevantes según el modelo seleccionado.
        
        Args:
            n (int, optional): Número de clientes para calcular Pn.
            
        Returns:
            dict: Diccionario con todos los resultados calculados.
        """
        results = {}
        
        try:
            # Cálculos básicos comunes a todos los modelos
            results['ro'] = self.calcular_ro()
            results['P0'] = self.calcular_P0()
            
            # Cálculos específicos según el modelo
            if n is not None:
                results[f'P{n}'] = self.calcular_Pn(n)
            
            if self.op == 1:  # PICS
                # Verificar estabilidad para M/M/1
                if not self.es_estable():
                    raise ValueError("El sistema no es estable")
                    
                results['L'] = self.calcular_L()
                results['Lq'] = self.calcular_Lq()
                results['Ln'] = self.calcular_Ln()
                results['W'] = self.calcular_W()
                results['Wq'] = self.calcular_Wq()
                results['Wn'] = self.calcular_Wn()
                
            elif self.op == 2:  # PICM
                results['Pk'] = self.calcular_Pk()
                results['L'] = self.calcular_L()
                results['Lq'] = self.calcular_Lq()
                results['Ln'] = self.calcular_Ln()
                results['W'] = self.calcular_W()
                results['Wq'] = self.calcular_Wq()
                results['Wn'] = self.calcular_Wn()
                
            elif self.op == 3:  # PFCS
                results['PE'] = self.calcular_PE()
                results['L'] = self.calcular_L()
                results['Lq'] = self.calcular_Lq()
                results['Ln'] = self.calcular_Ln()
                results['W'] = self.calcular_W()
                results['Wq'] = self.calcular_Wq()
                results['Wn'] = self.calcular_Wn()
                
            elif self.op == 4:  # PFCM
                results['PE'] = self.calcular_PE()
                results['PNE'] = self.calcular_PNE()
                results['L'] = self.calcular_L()
                results['Lq'] = self.calcular_Lq()
                results['Ln'] = self.calcular_Ln()
                results['W'] = self.calcular_W()
                results['Wq'] = self.calcular_Wq()
                results['Wn'] = self.calcular_Wn()
            
            return results
        
        except Exception as e:
            raise ValueError(f"Error en los cálculos: {str(e)}")
        
        