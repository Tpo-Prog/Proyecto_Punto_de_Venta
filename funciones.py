import pyodbc
from db import get_db_connection
from datetime import datetime
import hashlib
from decimal import Decimal, InvalidOperation

print("[DEBUG] Iniciando funciones.py...")


def agregar_articulo(codigo, descripcion, precio, stock, id_proveedor):
    conn, cursor = get_db_connection()
    if not conn: return
    try:
        sql = "INSERT INTO articulos (codigo, descripcion, precio, stock, id_proveedor) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql, (codigo, descripcion, precio, stock, id_proveedor))
        conn.commit()
    except Exception as e:
        print(f"Error al agregar el artículo: {e}")
    finally:
        if conn: conn.close()

def buscar_articulo(texto_busqueda):
    conn, cursor = get_db_connection()
    if not conn: return []
    try:
        sql = "SELECT * FROM articulos WHERE codigo = ? OR descripcion LIKE ?"
        cursor.execute(sql, (texto_busqueda, '%' + texto_busqueda + '%'))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al buscar artículos: {e}")
        return []
    finally:
        if conn: conn.close()


def listar_articulos():
    conn, cursor = get_db_connection()
    if not conn: return []
    try:
        # Unimos con proveedores para obtener el nombre
        sql = """
            SELECT 
                a.id, a.codigo, a.descripcion, a.precio, a.stock,
                a.id_proveedor, 
                ISNULL(p.nombre, 'Sin Proveedor') AS nombre_proveedor
            FROM articulos a
            LEFT JOIN proveedores p ON a.id_proveedor = p.id
            ORDER BY a.descripcion
        """
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al listar artículos: {e}")
        return []
    finally:
        if conn: conn.close()


def editar_articulo(id, codigo, descripcion, precio, stock, id_proveedor):
    conn, cursor = get_db_connection()
    if not conn: return
    try:
        sql = "UPDATE articulos SET codigo = ?, descripcion = ?, precio = ?, stock = ?, id_proveedor = ? WHERE id = ?"
        cursor.execute(sql, (codigo, descripcion, precio, stock, id_proveedor, id))
        conn.commit()
    except Exception as e:
        print(f"Error al editar el artículo: {e}")
    finally:
        if conn: conn.close()

def borrar_articulo(id):
    conn, cursor = get_db_connection()
    if not conn: return
    try:
        cursor.execute("DELETE FROM articulos WHERE id = ?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error al borrar el artículo: {e}")
    finally:
        if conn: conn.close()

def obtener_articulos():
    conn, cursor = get_db_connection()
    if not conn: return []
    try:
        cursor.execute("SELECT id, descripcion, precio FROM articulos ORDER BY descripcion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener artículos: {e}")
        return []
    finally:
        if conn: conn.close()

class Ticket:
    def __init__(self, punto_venta, metodo_pago, monto, fecha, tipo_ticket, referencia, id_caja=None):
        self.punto_venta = punto_venta
        self.metodo_pago = metodo_pago
        self.monto = monto
        self.fecha = fecha
        self.tipo_ticket = tipo_ticket
        self.referencia = referencia
        self.id_caja = id_caja
        self.id = None

    def guardar(self):
        conn, cursor = get_db_connection()
        if not conn: return
        try:
            sql = "INSERT INTO tickets (punto_venta, metodo_pago, monto, fecha, tipo_ticket, referencia, id_caja) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(sql, (self.punto_venta, self.metodo_pago, self.monto, self.fecha, self.tipo_ticket, self.referencia, self.id_caja))
            conn.commit()
            cursor.execute("SELECT @@IDENTITY AS id")
            self.id = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error al guardar el ticket: {e}")
        finally:
            if conn: conn.close()

    def guardar_detalle(self, detalle):
        conn, cursor = get_db_connection()
        if not conn: return
        try:
            for item in detalle:
                id_articulo, precio, cantidad, nombre = item
                sql = "INSERT INTO detalle_ticket (id_ticket, id_articulo, cantidad, precio_unitario, nombre_articulo) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (self.id, id_articulo, cantidad, precio, nombre))
            conn.commit()
        except Exception as e:
            print(f"Error al guardar el detalle del ticket: {e}")
        finally:
            if conn: conn.close()

def verificar_caja_abierta():
    print("[DEBUG] funciones.py: Llamando a verificar_caja_abierta()...")
    conn, cursor = get_db_connection()
    if not conn: return None
    try:
        cursor.execute("SELECT id, monto_inicial FROM caja WHERE estado = 'abierta'")
        resultado = cursor.fetchone()
        print(f"[DEBUG] funciones.py: verificar_caja_abierta() encontró: {resultado}")
        return resultado
    except Exception as e:
        print(f"Error al verificar el estado de la caja: {e}")
        return None
    finally:
        if conn: conn.close()

def abrir_caja(monto_inicial):
    print("[DEBUG] funciones.py: Llamando a abrir_caja()...")
    conn, cursor = get_db_connection()
    if not conn: return None
    try:
        sql = "INSERT INTO caja (fecha_apertura, monto_inicial, estado) VALUES (?, ?, ?)"
        cursor.execute(sql, (datetime.now(), monto_inicial, 'abierta'))
        conn.commit()
        cursor.execute("SELECT @@IDENTITY AS id")
        id_creado = cursor.fetchone()[0]
        print(f"[DEBUG] funciones.py: Caja abierta con ID: {id_creado}")
        return id_creado
    except Exception as e:
        print(f"Error al abrir caja: {e}")
        return None
    finally:
        if conn: conn.close()

def obtener_ventas_sesion(id_sesion):
    conn, cursor = get_db_connection()
    if not conn: return {}
    try:
        cursor.execute("SELECT fecha_apertura FROM caja WHERE id = ?", (id_sesion,))
        resultado = cursor.fetchone()
        if not resultado: return {}
        fecha_apertura = resultado[0]

        sql = "SELECT metodo_pago, SUM(monto) FROM tickets WHERE fecha >= ? AND id_caja = ? GROUP BY metodo_pago"
        cursor.execute(sql, (fecha_apertura, id_sesion))
        
        ventas = {"Efectivo": Decimal("0.0"), "Tarjeta": Decimal("0.0"), "Otros": Decimal("0.0")}
        for metodo, total in cursor.fetchall():
            if total is None: continue
            if metodo == 'Efectivo':
                ventas['Efectivo'] += total
            elif metodo in ('Tarjeta', 'Cuenta Corriente'):
                ventas['Tarjeta'] += total
            else:
                ventas['Otros'] += total
        return ventas
    except Exception as e:
        print(f"Error al obtener ventas de la sesión: {e}")
        return {}
    finally:
        if conn: conn.close()

def cerrar_caja(id_sesion, monto_inicial, monto_final_real, ventas_sesion):
    conn, cursor = get_db_connection()
    if not conn: return
    try:
        monto_inicial_dec = Decimal(str(monto_inicial))
        monto_final_real_dec = Decimal(str(monto_final_real))
        ventas_efectivo = ventas_sesion.get("Efectivo", Decimal("0.0"))

        monto_final_esperado = monto_inicial_dec + ventas_efectivo
        diferencia = monto_final_real_dec - monto_final_esperado
        
        sql = """
            UPDATE caja SET fecha_cierre = ?, total_ventas_efectivo = ?, 
            total_ventas_tarjeta = ?, total_ventas_otros = ?, monto_final_esperado = ?, 
            monto_final_real = ?, diferencia = ?, estado = 'cerrada'
            WHERE id = ? """
        cursor.execute(sql, (
            datetime.now(), 
            ventas_efectivo, 
            ventas_sesion.get("Tarjeta", Decimal("0.0")),
            ventas_sesion.get("Otros", Decimal("0.0")), 
            monto_final_esperado, 
            monto_final_real_dec, 
            diferencia, 
            id_sesion
        ))
        conn.commit()
        print("Caja cerrada exitosamente.")
    except Exception as e:
        print(f"Error al cerrar la caja: {e}")
    finally:
        if conn: conn.close()



def agregar_proveedor(nombre, cuit, telefono, email, direccion, notas):
    conn, cursor = get_db_connection()
    if not conn: 
        raise Exception("No se pudo conectar a la base de datos.")
    try:
        sql = "INSERT INTO proveedores (nombre, cuit, telefono, email, direccion, notas) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (nombre, cuit, telefono, email, direccion, notas))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al agregar el proveedor: {e}")
        raise Exception(f"Error al agregar el proveedor: {e}")
    finally:
        if conn: conn.close()

def listar_proveedores():
    conn, cursor = get_db_connection()
    if not conn: 
        raise Exception("No se pudo conectar a la base de datos.") 
    try:
        cursor.execute("SELECT id, nombre, cuit, telefono, email, direccion, notas FROM proveedores ORDER BY nombre")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al listar proveedores: {e}")
        raise Exception(f"Error al listar proveedores: {e}")
    finally:
        if conn: conn.close()

def editar_proveedor(id, nombre, cuit, telefono, email, direccion, notas):
    conn, cursor = get_db_connection()
    if not conn: 
        raise Exception("No se pudo conectar a la base de datos.")
    try:
        sql = """
            UPDATE proveedores 
            SET nombre = ?, cuit = ?, telefono = ?, email = ?, direccion = ?, notas = ?
            WHERE id = ?
        """
        cursor.execute(sql, (nombre, cuit, telefono, email, direccion, notas, id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al editar el proveedor: {e}")
        raise Exception(f"Error al editar el proveedor: {e}") 
    finally:
        if conn: conn.close()

def borrar_proveedor(id):
    conn, cursor = get_db_connection()
    if not conn: 
        raise Exception("No se pudo conectar a la base de datos.")
    try:
        cursor.execute("DELETE FROM proveedores WHERE id = ?", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al borrar el proveedor: {e}")
        raise Exception(f"Error al borrar el proveedor: {e}") 
    finally:
        if conn: conn.close()



def hash_password(password):
    """Genera un hash SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verificar_usuario(username, password):
    print(f"[DEBUG] funciones.py: Llamando a verificar_usuario() para usuario: {username}")
    conn, cursor = get_db_connection()
    if not conn: 
        print("[ERROR] funciones.py: verificar_usuario no pudo obtener conexión.")
        return None
    
    try:
        # Buscamos al usuario
        print(f"[DEBUG] funciones.py: Ejecutando SELECT sobre tabla 'usuarios'...")
        cursor.execute("SELECT password_hash, nombre_completo, rol FROM usuarios WHERE username = ?", (username,))
        usuario = cursor.fetchone()
        print(f"[DEBUG] funciones.py: Consulta a BD devolvió: {usuario}")
        
        if usuario:
            # Si el usuario existe, hasheamos la contraseña ingresada
            password_ingresada_hash = hash_password(password)
            
            # Comparamos el hash de la BD con el hash que acabamos de crear
            if password_ingresada_hash == usuario.password_hash:
                print("[DEBUG] funciones.py: ¡Contraseña VÁLIDA!")
                return {"nombre": usuario.nombre_completo, "rol": usuario.rol}
            else:
                print("[DEBUG] funciones.py: Contraseña INCORRECTA.")
        
        # Si el usuario no existe o la contraseña es incorrecta
        print("[DEBUG] funciones.py: Usuario no encontrado o contraseña no coincide.")
        return None
        
    except Exception as e:
        print(f"[ERROR] funciones.py: Error al verificar usuario: {e}")
        print("    Asegúrate de que la tabla 'usuarios' exista. Ejecuta 'ejecutame_primero_siosi.py'.")
        return None
    finally:
        if conn:
            print("[DEBUG] funciones.py: Cerrando conexión de verificar_usuario.")
            conn.close()

def listar_usuarios():
    """Obtiene todos los usuarios de la base de datos (sin el hash)."""
    print("[DEBUG] funciones.py: Llamando a listar_usuarios()...")
    conn, cursor = get_db_connection()
    if not conn: 
        print("[ERROR] funciones.py: listar_usuarios no pudo obtener conexión.")
        return []
    try:
        # Seleccionamos id, username, nombre_completo, rol (NO el password_hash)
        cursor.execute("SELECT id, username, nombre_completo, rol FROM usuarios ORDER BY username")
        usuarios = cursor.fetchall()
        print(f"[DEBUG] funciones.py: listar_usuarios encontró {len(usuarios)} usuarios.")
        return usuarios
    except Exception as e:
        print(f"[ERROR] funciones.py: Error al listar usuarios: {e}")
        return []
    finally:
        if conn:
            print("[DEBUG] funciones.py: Cerrando conexión de listar_usuarios.")
            conn.close()

def agregar_usuario(username, nombre, rol, password):
    """Agrega un nuevo usuario a la base de datos, hasheando la contraseña."""
    print(f"[DEBUG] funciones.py: Llamando a agregar_usuario() para '{username}'...")
    conn, cursor = get_db_connection()
    if not conn: 
        print("[ERROR] funciones.py: agregar_usuario no pudo obtener conexión.")
        raise Exception("No se pudo conectar a la base de datos.") 
    
    if not username or not password or not rol:
         raise ValueError("Username, Rol y Contraseña son obligatorios para nuevos usuarios.")

    try:
        # Hashear la contraseña antes de guardarla
        password_hash = hash_password(password)
        print("[DEBUG] funciones.py: Contraseña hasheada.")
        
        sql = "INSERT INTO usuarios (username, nombre_completo, rol, password_hash) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (username, nombre, rol, password_hash))
        conn.commit()
        print(f"[DEBUG] funciones.py: Usuario '{username}' agregado exitosamente.")
    except pyodbc.IntegrityError:
         # Error común si el username ya existe (UNIQUE constraint)
         print(f"[ERROR] funciones.py: Error de integridad al agregar '{username}' (¿Username duplicado?).")
         raise Exception(f"El username '{username}' ya existe.") 
    except Exception as e:
        print(f"[ERROR] funciones.py: Error al agregar usuario '{username}': {e}")
        conn.rollback() 
        raise Exception(f"Error inesperado al agregar usuario: {e}") 
    finally:
        if conn:
            print("[DEBUG] funciones.py: Cerrando conexión de agregar_usuario.")
            conn.close()

def editar_usuario(id_usuario, username, nombre, rol, password=None):
    """Edita un usuario existente. Solo actualiza la contraseña si se proporciona una nueva."""
    print(f"[DEBUG] funciones.py: Llamando a editar_usuario() para ID: {id_usuario}...")
    conn, cursor = get_db_connection()
    if not conn: 
        print("[ERROR] funciones.py: editar_usuario no pudo obtener conexión.")
        raise Exception("No se pudo conectar a la base de datos.")
        
    if not id_usuario or not username or not rol:
         raise ValueError("ID, Username y Rol son obligatorios para editar.")

    
    if username == 'admin':
         print("[WARN] funciones.py: Intento de editar datos críticos del usuario 'admin'. Se permite cambio de nombre/rol/pass, no username.")
         
    try:
        if password: # Si se proporcionó una nueva contraseña
            print("[DEBUG] funciones.py: Se proporcionó nueva contraseña. Hasheando...")
            password_hash = hash_password(password)
            sql = """UPDATE usuarios 
                     SET nombre_completo = ?, rol = ?, password_hash = ? 
                     WHERE id = ? AND username = ?""" # Usamos username como seguridad extra
            params = (nombre, rol, password_hash, id_usuario, username)
        else: # No se proporcionó contraseña, no la actualizamos
            print("[DEBUG] funciones.py: No se proporcionó nueva contraseña. Se mantiene la actual.")
            sql = """UPDATE usuarios 
                     SET nombre_completo = ?, rol = ? 
                     WHERE id = ? AND username = ?"""
            params = (nombre, rol, id_usuario, username)
            
        cursor.execute(sql, params)
        
        # Verificar si se actualizó alguna fila
        if cursor.rowcount == 0:
             print(f"[ERROR] funciones.py: No se encontró el usuario con ID {id_usuario} y Username '{username}' para editar.")
             raise Exception("Usuario no encontrado o no se pudo editar (¿Username incorrecto?).")
             
        conn.commit()
        print(f"[DEBUG] funciones.py: Usuario ID {id_usuario} editado exitosamente.")
    except Exception as e:
        print(f"[ERROR] funciones.py: Error al editar usuario ID {id_usuario}: {e}")
        conn.rollback()
        raise Exception(f"Error inesperado al editar usuario: {e}")
    finally:
        if conn:
            print("[DEBUG] funciones.py: Cerrando conexión de editar_usuario.")
            conn.close()

def borrar_usuario(id_usuario):
    """Elimina un usuario de la base de datos."""
    print(f"[DEBUG] funciones.py: Llamando a borrar_usuario() para ID: {id_usuario}...")
    conn, cursor = get_db_connection()
    if not conn: 
        print("[ERROR] funciones.py: borrar_usuario no pudo obtener conexión.")
        raise Exception("No se pudo conectar a la base de datos.")

    if not id_usuario:
        raise ValueError("Se requiere un ID para borrar el usuario.")

    try:
        cursor.execute("SELECT username FROM usuarios WHERE id = ?", (id_usuario,))
        user_result = cursor.fetchone()
        if user_result and user_result.username == 'admin':
             print("[ERROR] funciones.py: Intento de borrar al usuario 'admin'. OPERACIÓN DENEGADA.")
             raise Exception("No se puede eliminar al usuario administrador principal ('admin').")

        # Si no es admin, proceder a borrar
        sql = "DELETE FROM usuarios WHERE id = ?"
        cursor.execute(sql, (id_usuario,))
        
        if cursor.rowcount == 0:
             print(f"[ERROR] funciones.py: No se encontró el usuario con ID {id_usuario} para borrar.")
             raise Exception("Usuario no encontrado para eliminar.")
             
        conn.commit()
        print(f"[DEBUG] funciones.py: Usuario ID {id_usuario} borrado exitosamente.")
    except Exception as e:
        print(f"[ERROR] funciones.py: Error al borrar usuario ID {id_usuario}: {e}")
        conn.rollback()
        raise e 
    finally:
        if conn:
            print("[DEBUG] funciones.py: Cerrando conexión de borrar_usuario.")
            conn.close()

print("[DEBUG] funciones.py: Archivo importado.")