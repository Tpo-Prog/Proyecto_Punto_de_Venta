import pyodbc
from db import get_db_connection

def cargar_datos_prueba():
    conn, cursor = get_db_connection()
    if not conn:
        print("❌ No se pudo obtener conexión. Abortando.")
        return

    try:
        # --- 1. Cargar Proveedores de Prueba ---
        print("🔄 Cargando proveedores de prueba...")
        
        proveedores = [
            # ID 1 (esperado)
            ('Distribuidora Bebidas Cuyo', '30-11111111-1', '261-111-1111', 'compras@bebidascuyo.com', 'Av. Siempre Viva 123', 'Entrega lunes y jueves'),
            # ID 2 (esperado)
            ('TecnoMundo S.A.', '30-22222222-2', '11-2222-2222', 'ventas@tecnomundo.com', 'Calle Falsa 123', 'Garantía 1 año'),
            # ID 3 (esperado)
            ('Librería El Estudiante', '30-33333333-3', '11-3333-3333', 'info@libreriaestudiante.com', 'Av. Corrientes 456', 'Descuento por volumen')
        ]
        
        sql_prov = """
            IF NOT EXISTS (SELECT 1 FROM proveedores WHERE cuit = ?)
            INSERT INTO proveedores (nombre, cuit, telefono, email, direccion, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        
        for p in proveedores:
            # p[1] es el CUIT. El *p expande todos los 6 argumentos para el INSERT
            cursor.execute(sql_prov, (p[1], *p))
        
        print("✅ Proveedores de prueba cargados (o ya existían).")


        # --- 2. Cargar Artículos de Prueba (con id_proveedor) ---
        print("🔄 Cargando artículos de prueba...")
        
        # Asignamos IDs de proveedor (1, 2, 3) o None
        articulos = [
          ("001", "Pepsi 1.5L", 450.00, 30, 1),
          ("002", "Agua 500ml", 300.00, 50, 1),
          ("290", "Alto-Guiso", 1500.00, 20, None),
          ("444", "Monster - Cargada desde la pc de Ivan", 2400.00, 100, 1),
          ("555", "Test para villa", 10000.00, 100, None),
          ("202", "Pastel-de-papa", 2000.00, 50000, None),
          ("423", "cargado-desde-abril", 5000.00, 1, None),
          ("137", "you-got-the-best-of-me", 1343.40, 2013, None),
          ("303", "alfajorcito-el-gordito", 100.00, 1, None),
          ("TEC001", "Mouse inalámbrico Logitech", 4500.00, 50, 2),
          ("TEC002", "Teclado mecánico Redragon", 9800.00, 30, 2),
          ("TEC003", "Auriculares Bluetooth JBL", 12500.00, 40, 2),
          ("TEC004", "Monitor LED 24\" Samsung", 62000.00, 15, 2),
          ("TEC005", "Cable USB-C reforzado", 1800.00, 100, 2),
          ("TEC006", "Cargador portátil 10000mAh", 5200.00, 25, 2),
          ("TEC007", "Soporte notebook ajustable", 3100.00, 40, 2),
          ("TEC008", "Hub USB 4 puertos", 2700.00, 35, 2),
          ("TEC009", "Webcam HD Logitech", 8900.00, 20, 2),
          ("TEC010", "Parlante Bluetooth Xiaomi", 15800.00, 16, 2),
          ("ALI001", "Pack de 6 aguas saborizadas", 2100.00, 60, 1),
          ("ALI002", "Caja de alfajores artesanales", 3500.00, 25, None),
          ("ALI003", "Yerba mate 1kg Taragüí", 1800.00, 80, None),
          ("ALI004", "Café molido La Virginia 500g", 2200.00, 45, None),
          ("ALI005", "Galletitas surtidas 500g", 950.00, 70, None),
          ("ALI006", "Arroz largo fino 1kg", 750.00, 100, None),
          ("ALI007", "Aceite de girasol 900ml", 1200.00, 60, None),
          ("ALI008", "Fideos tirabuzón 500g", 650.00, 90, None),
          ("ALI009", "Salsa lista tomate 340g", 980.00, 50, None),
          ("ALI010", "Azúcar común 1kg", 780.00, 85, None),
          ("LIB001", "Cuaderno tapa dura 100 hojas", 1100.00, 75, 3),
          ("LIB002", "Lapicera gel negra x3", 750.00, 90, 3),
          ("LIB003", "Resaltadores pastel x5", 1350.00, 40, 3),
          ("LIB004", "Agenda semanal 2025", 2100.00, 30, 3),
          ("LIB005", "Cartuchera triple compartimiento", 2400.00, 20, 3),
          ("LIB006", "Block de hojas A4", 950.00, 60, 3),
          ("LIB007", "Corrector líquido x2", 680.00, 45, 3),
          ("LIB008", "Set de lápices de colores x12", 1200.00, 50, 3),
          ("LIB009", "Regla flexible 30cm", 400.00, 80, 3),
          ("LIB010", "Marcadores permanentes x4", 890.00, 35, 3),
          ("HOG001", "Set de vasos térmicos x4", 4300.00, 25, None),
          ("HOG002", "Toalla de baño premium", 2700.00, 50, None),
          ("HOG003", "Lámpara LED escritorio", 5200.00, 22, None),
          ("HOG004", "Organizador multiuso plástico", 1600.00, 60, None),
          ("HOG005", "Cortina blackout 1.40x2.00", 8900.00, 10, None),
          ("HOG006", "Almohada viscoelástica", 3400.00, 30, None),
          ("HOG007", "Set de cubiertos x24", 7800.00, 18, None),
          ("HOG008", "Cesto de ropa plegable", 2100.00, 40, None),
          ("HOG009", "Reloj de pared moderno", 3200.00, 25, None),
          ("HOG010", "Porta especias giratorio", 2900.00, 20, None),
          ("IND011", "Buzo canguro unisex", 7400.00, 28, None),
          ("IND012", "Medias deportivas x3", 1800.00, 60, None),
          ("IND013", "Camisa casual manga larga", 6200.00, 22, None),
          ("IND014", "Short de baño estampado", 4100.00, 30, None),
          ("IND015", "Cinturón cuero clásico", 3500.00, 15, None),
          ("IND016", "Vestido de verano estampado", 8900.00, 12, None),
          ("IND017", "Pijama algodón adulto", 5200.00, 20, None),
          ("IND018", "Bufanda tejida artesanal", 3100.00, 25, None),
          ("IND019", "Guantes térmicos invierno", 2700.00, 18, None),
          ("IND020", "Campera inflable liviana", 11500.00, 10, None),
          ("HER011", "Destornillador multipunta", 2100.00, 40, None),
          ("HER012", "Martillo carpintero 16oz", 3200.00, 25, None),
          ("HER013", "Llave ajustable 10\"", 2800.00, 30, None),
          ("HER014", "Cinta métrica 5m", 950.00, 50, None),
          ("HER015", "Nivel de burbuja 30cm", 1100.00, 35, None),
          ("HER016", "Taladro eléctrico 650W", 18500.00, 10, None),
          ("HER017", "Caja de herramientas básica", 9200.00, 12, None),
          ("HER018", "Pinza universal 8\"", 1600.00, 40, None),
          ("HER019", "Juego de llaves Allen x10", 1400.00, 45, None),
          ("HER020", "Sierra manual para madera", 2100.00, 20, None),
          ("JUG011", "Set de bloques didácticos", 3200.00, 30, None),
          ("JUG012", "Muñeca articulada con accesorios", 5800.00, 20, None),
          ("JUG013", "Auto a fricción metálico", 2700.00, 40, None),
          ("JUG014", "Pelota de fútbol infantil", 1900.00, 35, None),
          ("JUG015", "Rompecabezas 500 piezas", 2400.00, 25, None),
          ("JUG016", "Juego de mesa familiar", 6200.00, 18, None),
          ("JUG017", "Set de pinturas lavables", 1500.00, 50, None),
          ("JUG018", "Libro de cuentos ilustrado", 1800.00, 40, None),
          ("JUG019", "Pistola de burbujas recargable", 2100.00, 30, None),
          ("JUG020", "Masa moldeable x6 colores", 1300.00, 60, None),
          ("LIM011", "Detergente concentrado 750ml", 950.00, 80, None),
          ("LIM012", "Lavandina perfumada 1L", 780.00, 70, None),
          ("LIM013", "Desinfectante multiuso 500ml", 1200.00, 60, None),
          ("LIM014", "Esponja doble acción x2", 650.00, 90, None),
          ("LIM015", "Trapo de piso absorbente", 1100.00, 50, None),
          ("LIM016", "Limpiavidrios con gatillo", 1400.00, 40, None),
          ("LIM017", "Cepillo de mano ergonómico", 850.00, 45, None),
          ("LIM018", "Guantes de látex x2", 700.00, 60, None),
          ("LIM019", "Bolsa de residuos 30L x10", 950.00, 55, None),
          ("LIM020", "Ambientador aerosol lavanda", 1200.00, 35, None),
          ("MAS011", "Bolsa de alimento perro 3kg", 4200.00, 25, None),
          ("MAS012", "Pelota mordedora resistente", 1100.00, 40, None),
          ("MAS013", "Collar ajustable mediano", 1800.00, 30, None),
          ("MAS014", "Comedero doble plástico", 2200.00, 20, None),
          ("MAS015", "Shampoo neutro 250ml", 1500.00, 35, None),
          ("MAS016", "Bolsitas higiénicas x50", 950.00, 45, None),
          ("MAS017", "Cama acolchada para mascotas", 7800.00, 15, None),
          ("MAS018", "Juguete chirriante en forma de hueso", 1300.00, 50, None),
          ("MAS019", "Arnés ajustable con correa", 3200.00, 18, None),
          ("MAS020", "Cepillo de pelo para mascotas", 2100.00, 22, None)                        
         ]

        sql_art = """
            IF NOT EXISTS (SELECT 1 FROM articulos WHERE codigo = ?)
            INSERT INTO articulos (codigo, descripcion, precio, stock, id_proveedor)
            VALUES (?, ?, ?, ?, ?)
        """
        
        count = 0
        for art in articulos:
            # art[0] es el Código. El *art expande los 5 argumentos para el INSERT
            cursor.execute(sql_art, (art[0], *art))
            if cursor.rowcount > 0:
                count += 1
        
        print(f"✅ Se insertaron {count} artículos nuevos.")
        
        conn.commit()
        print("🎉 ¡Base de datos lista con datos de prueba!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al cargar datos de prueba: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Iniciando carga de datos de prueba...")
    cargar_datos_prueba()