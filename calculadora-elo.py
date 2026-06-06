# 25 mayo 2021
# J3, Emperor Cup

# 9 junio 2021
# J1, J2, J. League Cup

import csv
import os

CSV_FILE = 'elo-jp.csv'

def cargar_elos(archivo):
    elos = {}
    if not os.path.exists(archivo):
        return elos
    with open(archivo, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 3:
                continue
            equipo = row[0].strip()
            elo_str = row[1].strip()
            liga = row[2].strip()
            
            # Validar cabecera y tipos de datos
            if equipo.lower() == 'team' or equipo == '' or not elo_str.replace('.', '', 1).replace('-', '', 1).isdigit():
                continue
            
            # Guardamos el elo y la liga correspondientes
            elos[equipo] = {'elo': float(elo_str), 'league': liga}
    return elos

def guardar_elos(archivo, elos):
    with open(archivo, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Team', 'Elo', 'League'])
        for equipo, datos in elos.items():
            elo = datos['elo']
            liga = datos['league']
            elo_formateado = int(elo) if elo.is_integer() else elo
            writer.writerow([equipo, elo_formateado, liga])

def buscar_equipo(entrada, elos):
    entrada_baja = entrada.lower()
    exactos = [eq for eq in elos if eq.lower() == entrada_baja]
    if exactos:
        return exactos[0]
    
    empiezan = [eq for eq in elos if eq.lower().startswith(entrada_baja)]
    if len(empiezan) == 1:
        print(f" -> Autocompletado: {empiezan[0]}")
        return empiezan[0]
    elif len(empiezan) > 1:
        print(f"⚠️ Múltiples equipos coinciden con '{entrada}': {', '.join(empiezan)}")
        return "MULTIPLE"
    return None

def calcular_nuevo_elo(elo_local, elo_visitante, goles_local, goles_visitante, competicion):
    k_factors = {
        'J1': 30, 'J2': 25, 'J3': 20,
        'Emperor Cup': 35, 'J. League Cup': 20
    }
    
    K = k_factors.get(competicion, 25)
    ventaja_local = 30
    elo_local_ajustado = elo_local + ventaja_local
    
    # Probabilidad Esperada (We)
    we_local = 1 / (10 ** (-(elo_local_ajustado - elo_visitante) / 400) + 1)
    we_visitante = 1 - we_local
    
    # Resultado Real (W)
    diferencia_goles = abs(goles_local - goles_visitante)
    if goles_local > goles_visitante:
        w_local, w_visitante = 1.0, 0.0
    elif goles_local < goles_visitante:
        w_local, w_visitante = 0.0, 1.0
    else:
        w_local, w_visitante = 0.5, 0.5
        
    # Multiplicador de Margen de Goles (G)
    if diferencia_goles <= 1:
        G = 1.0
    elif diferencia_goles == 2:
        G = 1.5
    else:
        G = (11 + diferencia_goles) / 8.0
        
    # Cálculo Final
    nuevo_elo_local = elo_local + (K * G) * (w_local - we_local)
    nuevo_elo_visitante = elo_visitante + (K * G) * (w_visitante - we_visitante)
    
    return round(nuevo_elo_local, 0), round(nuevo_elo_visitante, 0)

def iniciar_calculadora():
    print("==================================================")
    print("🏆 CALCULADORA ELO INTERACTIVA (VANILLA PYTHON) 🏆")
    print("==================================================")
    print("Escribe 'salir' en cualquier momento para cerrar.\n")
    
    diccionario_competiciones = {
        '1': 'J1', '2': 'J2', '3': 'J3',
        '4': 'Emperor Cup', '5': 'J. League Cup'
    }

    # Corregido el desempaquetado de variables
    elos = cargar_elos(CSV_FILE)

    while True:
        try:
            # 1. Input Equipo Local
            entrada_local = input("Nombre del equipo LOCAL: ").strip()
            if entrada_local.lower() == 'salir': 
                break
            
            equipo_local = buscar_equipo(entrada_local, elos)
            if equipo_local == "MULTIPLE":
                continue
            if not equipo_local:
                crear = input(f"Equipo '{entrada_local}' no encontrado. ¿Añadir nuevo? (s/n): ").strip().lower()
                if crear == 's':
                    elo_local = float(input(f"Elo inicial para {entrada_local}: "))
                    liga_local = input(f"Liga para {entrada_local} (ej. J1, J2): ").strip()
                    equipo_local = entrada_local
                    elos[equipo_local] = {'elo': elo_local, 'league': liga_local}
                else:
                    continue
            else:
                elo_local = elos[equipo_local]['elo']
            
            # 2. Input Equipo Visitante
            entrada_visitante = input("Nombre del equipo VISITANTE: ").strip()
            if entrada_visitante.lower() == 'salir': 
                break
            
            equipo_visitante = buscar_equipo(entrada_visitante, elos)
            if equipo_visitante == "MULTIPLE":
                continue
            if not equipo_visitante:
                crear = input(f"Equipo '{entrada_visitante}' no encontrado. ¿Añadir nuevo? (s/n): ").strip().lower()
                if crear == 's':
                    elo_visitante = float(input(f"Elo inicial para {entrada_visitante}: "))
                    liga_visitante = input(f"Liga para {entrada_visitante} (ej. J1, J2): ").strip()
                    equipo_visitante = entrada_visitante
                    elos[equipo_visitante] = {'elo': elo_visitante, 'league': liga_visitante}
                else:
                    continue
            else:
                elo_visitante = elos[equipo_visitante]['elo']
            
            # 3. Input Goles Local
            entrada_goles_l = input("Goles del LOCAL: ").strip().lower()
            if entrada_goles_l == 'salir': 
                break
            goles_local = int(entrada_goles_l)
            
            # 4. Input Goles Visitante
            entrada_goles_v = input("Goles del VISITANTE: ").strip().lower()
            if entrada_goles_v == 'salir': 
                break
            goles_visitante = int(entrada_goles_v)
            
            # 5. Selección de Competición
            print("\nCompeticiones disponibles:")
            print("1. J1  |  2. J2  |  3. J3  |  4. Emperor Cup  |  5. J. League Cup")
            opcion_comp = input("Selecciona el número de la competición: ").strip().lower()
            if opcion_comp == 'salir': 
                break
            
            competicion = diccionario_competiciones.get(opcion_comp, 'J2')
            
            # Ejecutar cálculo
            nuevo_local, nuevo_visitante = calcular_nuevo_elo(
                elo_local, elo_visitante, goles_local, goles_visitante, competicion
            )
            
            # Mostrar Resultados
            print("\n" + "-"*40)
            print("📊 RESULTADOS DE LA ACTUALIZACIÓN ELO")
            print("-" * 40)
            print(f"Competición: {competicion} | Resultado: {goles_local} - {goles_visitante}")
            
            diff_local = round(nuevo_local - elo_local, 0)
            diff_visitante = round(nuevo_visitante - elo_visitante, 0)
            
            signo_l = "+" if diff_local > 0 else ""
            signo_v = "+" if diff_visitante > 0 else ""
            
            print(f"🏠 {equipo_local}: {elo_local}  --->  {nuevo_local}  ({signo_l}{diff_local})")
            print(f"✈️ {equipo_visitante}: {elo_visitante}  --->  {nuevo_visitante}  ({signo_v}{diff_visitante})")
            print("-" * 40)
            
            # Guardar los nuevos Elos preservando la liga original
            elos[equipo_local]['elo'] = nuevo_local
            elos[equipo_visitante]['elo'] = nuevo_visitante
            
            # Corregido el llamado de la función (se removió 'leagues')
            guardar_elos(CSV_FILE, elos)
            print(f"✅ Elos guardados en {CSV_FILE}\n")
            
        except ValueError:
            print("\n⚠️ ERROR: Por favor ingresa un número válido. Inténtalo de nuevo.\n")
            continue
            
    print("\nCalculadora cerrada exitosamente.")

if __name__ == "__main__":
    iniciar_calculadora()