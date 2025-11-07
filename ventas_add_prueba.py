import pyodbc
import random
from datetime import datetime, timedelta
from db import get_db_connection
from funciones import Ticket, obtener_articulos, verificar_caja_abierta, abrir_caja
from decimal import Decimal

print("🔄 Iniciando carga de ventas de prueba...")

def obtener_caja_activa():
    """Verifica si hay una caja abierta, si no, abre una nueva."""
    print("Verificando caja...")
    caja = verificar_caja_abierta()
    if caja:
        print(f"✅ Usando caja existente ID: {caja[0]}")
        return caja[0] # Retorna el ID
    else:
        print("No hay caja abierta. Abriendo una nueva caja de prueba...")
        # Abrir caja con monto 0
        id_caja_nueva = abrir_caja(0.0)
        if id_caja_nueva:
            print(f"✅ Caja de prueba creada con ID: {id_caja_nueva}")
            return id_caja_nueva
        else:
            raise Exception("No se pudo crear una caja de prueba.")

def cargar_ventas_prueba(id_caja, num_tickets=150):
    print(f"Obteniendo lista de artículos...")
    # obtener_articulos() devuelve (id, descripcion, precio)
    articulos_disponibles = obtener_articulos() 
    if not articulos_disponibles:
        print("❌ No hay artículos en la base de datos. Ejecuta 'articulos_add.py' primero.")
        return

    print(f"Generando {num_tickets} tickets de prueba...")
    
    ticket_count = 0
    
    try:
        for i in range(num_tickets):
            # 1. Generar datos del Ticket
            metodo = random.choice(["Efectivo", "Tarjeta", "Transferencia", "Mercado Pago"])
            
            # --- Crucial: Generar fecha histórica ---
            dias_atras = random.randint(0, 30) # Ventas de los últimos 30 días
            minutos_atras = random.randint(0, 1440) # A diferentes horas
            fecha_ticket = datetime.now() - timedelta(days=dias_atras, minutes=minutos_atras)
            
            # 2. Generar Detalle del Ticket
            num_articulos_en_ticket = random.randint(1, 5)
            articulos_seleccionados = random.sample(articulos_disponibles, k=num_articulos_en_ticket)
            
            detalle = []
            monto_total = Decimal("0.0")

            for art in articulos_seleccionados:
                id_articulo = art[0]
                nombre_articulo = art[1]
                # Aseguramos que el precio sea Decimal para el cálculo
                precio_unitario = Decimal(str(art[2])) 
                cantidad = random.randint(1, 3)
                
                subtotal = precio_unitario * cantidad
                monto_total += subtotal
                # Guardamos el detalle como lo espera la función
                detalle.append((id_articulo, precio_unitario, cantidad, nombre_articulo))

            # 3. Guardar el Ticket
            # La clase Ticket convierte el monto a float internamente si es necesario
            ticket = Ticket(
                punto_venta="Local Principal",
                metodo_pago=metodo,
                monto=float(monto_total),
                fecha=fecha_ticket,
                tipo_ticket="Venta Prueba",
                referencia=f"PRUEBA-{random.randint(1000, 9999)}",
                id_caja=id_caja
            )
            
            # ticket.guardar() abre y cierra su propia conexión.
            ticket.guardar() # Esto guarda el ticket y obtiene ticket.id
            
            if ticket.id:
                # ticket.guardar_detalle() también gestiona su propia conexión.
                ticket.guardar_detalle(detalle) 
                ticket_count += 1
            else:
                print("Error al guardar ticket, no se generó ID.")

            if (i + 1) % 25 == 0:
                print(f"--- {i+1} tickets generados ---")

        print(f"✅ Se generaron y guardaron {ticket_count} tickets de prueba.")
        
    except Exception as e:
        print(f"❌ Error durante la generación de ventas: {e}")

if __name__ == "__main__":
    try:
        # Primero, asegurarnos que la BD está conectada y hay artículos
        conn, cursor = get_db_connection()
        if not conn:
             raise Exception("No se pudo conectar a la DB. Verifica config.py y SQL Server.")
        conn.close()
        
        id_caja_para_pruebas = obtener_caja_activa()
        if id_caja_para_pruebas:
            cargar_ventas_prueba(id_caja_para_pruebas, num_tickets=150)
        print("🎉 ¡Carga de ventas finalizada!")
    except Exception as e:
        print(f"❌ Error fatal en el script: {e}")