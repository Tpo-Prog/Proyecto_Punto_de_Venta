import pyodbc
from config import CONNECTION_STRING

print("[DEBUG] Iniciando ejecutame_primero_siosi.py...")

def get_db_connection():
    print("[DEBUG] ejecutame: Llamando a get_db_connection()...")
    try:
        print("[DEBUG] ejecutame: Intentando pyodbc.connect()...")
        conn = pyodbc.connect(CONNECTION_STRING)
        print("[DEBUG] ejecutame: Conexión CREADA.")
        return conn, conn.cursor()
    except Exception as e:
        print("❌ [ERROR] ejecutame: Error al conectar con la base:", e)
        return None, None

def crear_tablas():
    print("[DEBUG] ejecutame: Iniciando crear_tablas()...")
    conn, cursor = get_db_connection()
    if not conn:
        print("[ERROR] ejecutame: No hay conexión. Abortando creación de tablas.")
        return

    try:
        # --- Tabla de Proveedores (Debe existir ANTES que artículos) ---
        print("[DEBUG] ejecutame: Creando tabla 'proveedores'...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='proveedores' AND xtype='U')
        CREATE TABLE proveedores (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            cuit VARCHAR(20) UNIQUE,
            telefono VARCHAR(50),
            email VARCHAR(255),
            direccion VARCHAR(255),
            notas TEXT
        )
        """)

        # --- Tabla de Artículos 
        print("[DEBUG] ejecutame: Creando tabla 'articulos'...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='articulos' AND xtype='U')
        CREATE TABLE articulos (
            id INT IDENTITY(1,1) PRIMARY KEY,
            codigo VARCHAR(50) UNIQUE NOT NULL,
            descripcion VARCHAR(255) NOT NULL,
            precio DECIMAL(10, 2) NOT NULL,
            stock INT NOT NULL,
            id_proveedor INT,
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id) ON DELETE SET NULL
        )
        """)
        
        # --- Tabla de Caja ---
        print("[DEBUG] ejecutame: Creando tabla 'caja'...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='caja' AND xtype='U')
        CREATE TABLE caja (
            id INT IDENTITY(1,1) PRIMARY KEY,
            fecha_apertura DATETIME,
            fecha_cierre DATETIME,
            monto_inicial DECIMAL(10,2),
            total_ventas_efectivo DECIMAL(10,2),
            total_ventas_tarjeta DECIMAL(10,2),
            total_ventas_otros DECIMAL(10,2),
            monto_final_esperado DECIMAL(10,2),
            monto_final_real DECIMAL(10,2),
            diferencia DECIMAL(10,2),
            estado VARCHAR(20) -- puede ser 'abierta' o 'cerrada'
        )
        """)
        
        # --- Tabla de Tickets ---
        print("[DEBUG] ejecutame: Creando tabla 'tickets'...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tickets' AND xtype='U')
        CREATE TABLE tickets (
            id INT IDENTITY(1,1) PRIMARY KEY,
            fecha DATETIME DEFAULT GETDATE(),
            punto_venta VARCHAR(50) DEFAULT 'Desconocido',
            metodo_pago VARCHAR(30) DEFAULT 'Efectivo',
            tipo_ticket VARCHAR(30) DEFAULT 'General',
            monto DECIMAL(10,2) DEFAULT 0.00,
            referencia VARCHAR(50) DEFAULT 'Sin referencia',
            id_caja INT, 
            FOREIGN KEY (id_caja) REFERENCES caja(id) 
        )
        """)

        # --- Tabla de Detalle de Ticket ---
        print("[DEBUG] ejecutame: Creando tabla 'detalle_ticket'...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='detalle_ticket' AND xtype='U')
        CREATE TABLE detalle_ticket (
            id INT IDENTITY(1,1) PRIMARY KEY,
            id_ticket INT,
            id_articulo INT,
            cantidad INT,
            precio_unitario DECIMAL(10,2),
            nombre_articulo VARCHAR(255),
            FOREIGN KEY (id_ticket) REFERENCES tickets(id),
            FOREIGN KEY (id_articulo) REFERENCES articulos(id)
        )
        """)

        # --- Tabla de Usuarios ---
        print("[DEBUG] ejecutame: Creando tabla 'usuarios'...")
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U')
        CREATE TABLE usuarios (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            nombre_completo VARCHAR(255),
            rol VARCHAR(50) DEFAULT 'vendedor'
        )
        """)

        #usuario "admin" por defecto
        print("[DEBUG] ejecutame: Insertando usuario 'admin' (si no existe)...")
        cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM usuarios WHERE username = 'admin')
        INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
        VALUES ('admin', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'Administrador del Sistema', 'admin')
        """)

        print("[DEBUG] ejecutame: Aplicando 'COMMIT' a la base de datos...")
        conn.commit()
        print("✅ Tablas creadas o verificadas correctamente.")
    except Exception as e:
        print("❌ Error al crear tablas:", e)
    finally:
        if conn:
            print("[DEBUG] ejecutame: Cerrando conexión.")
            conn.close()

if __name__ == "__main__":
    print("🔄 Iniciando configuración de base de datos...")
    crear_tablas()
    print("🎉 ¡Base de datos lista!")|  