print("[DEBUG] Iniciando main.py (V3.3 - Import Corregido)...")
print("[DEBUG] main.py: Importando librerías...")
import tkinter as tk
from tkinter import ttk, messagebox
import funciones
from interfaz_tickets import creartickets

# --- MODIFICACIÓN DE IMPORTS ---
# Las funciones de graficos.py ya no se usan, importamos la nueva ventana
from interfaz_graficos import abrir_ventana_graficos
# --- FIN MODIFICACIÓN ---

from datetime import datetime
from generar_pdf_tkinter import abrir_ventana_pdf
from interfaz import ventana_cobro, mostrar_ultimos_tickets
from decimal import Decimal, InvalidOperation
from interfaz_proveedores import abrir_ventana_proveedores
from interfaz_login import LoginFrame
from interfaz_usuarios import abrir_ventana_gestion_usuarios
import traceback
print("[DEBUG] main.py: Imports terminados.")

class PuntoDeVentaApp:
    
    # --- CONSTANTE DE ALERTA DE STOCK ---
    LOW_STOCK_THRESHOLD = 10
    
    def __init__(self, root):
        print("[DEBUG] main.py: PuntoDeVentaApp.__init__ INICIADO.")
        self.root = root
        
        self.articulos_agregados = []
        self.checks_articulos = []
        self.id_sesion_actual = None
        self.monto_inicial_caja = Decimal("0.00")
        self.lista_articulos_completa = []
        self.mapa_articulos = {}
        self.usuario_actual = None
        self.login_frame = None
        self.main_widgets_created = False
        print("[DEBUG] main.py: __init__: Variables de instancia creadas.")

        print("[DEBUG] main.py: __init__: Creando LoginFrame...")
        self.login_frame = LoginFrame(master=self.root,
                                       on_success=self._on_login_success,
                                       on_cancel=self._on_login_cancel)
        self.login_frame.pack(fill="both", expand=True)
        print("[DEBUG] main.py: __init__: LoginFrame CREADO y mostrado.")
        
        print("[DEBUG] main.py: __init__ TERMINADO (esperando acción en LoginFrame).")

    def _on_login_success(self, usuario_info):
        """Callback llamado por LoginFrame cuando el login es exitoso."""
        print("[DEBUG] main.py: _on_login_success INICIADO.")
        self.usuario_actual = usuario_info
        print(f"Bienvenido {self.usuario_actual['nombre']} (Rol: {self.usuario_actual['rol']})")
        
        if self.login_frame:
            print("[DEBUG] main.py: Destruyendo LoginFrame...")
            self.login_frame.destroy()
            self.login_frame = None
            self.root.unbind('<Return>')
            self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        
        print("[DEBUG] main.py: Llamando a _iniciar_interfaz_principal...")
        self._iniciar_interfaz_principal()

    def _on_login_cancel(self):
        """Callback llamado por LoginFrame si se cancela."""
        print("[DEBUG] main.py: _on_login_cancel INICIADO. Cerrando aplicación.")
        self.root.destroy()

    def _iniciar_interfaz_principal(self):
        """Se llama después de un login exitoso para configurar la app principal."""
        print("[DEBUG] main.py: _iniciar_interfaz_principal INICIADO.")
        try:
            print("[DEBUG] main.py: Llamando a _ventana_apertura_caja...")
            caja_abierta_exitosamente = self._ventana_apertura_caja()
            print(f"[DEBUG] main.py: _ventana_apertura_caja devolvió: {caja_abierta_exitosamente}")
            
            if not caja_abierta_exitosamente:
                self.root.destroy()
                print("[DEBUG] main.py: Apertura de caja cancelada. App cerrada.")
                return

            # --- MEJORA: ABRIR MAXIMIZADO ---
            print("[DEBUG] main.py: Configurando ventana principal para maximizar...")
            try:
                self.root.state('zoomed') # Maximiza la ventana (Win/Linux)
            except tk.TclError:
                try:
                    self.root.wm_state('zoomed') # Intento alternativo (Win)
                except tk.TclError:
                     # Fallback si 'zoomed' no funciona (algunos Linux/macOS)
                    screen_width = self.root.winfo_screenwidth()
                    screen_height = self.root.winfo_screenheight()
                    self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.root.resizable(True, True)
            # --- FIN MEJORA ---
            
            if not self.main_widgets_created:
                print("[DEBUG] main.py: Llamando a _crear_widgets...")
                self._crear_widgets()
                self.main_widgets_created = True
                print("[DEBUG] main.py: _crear_widgets TERMINÓ.")
            else:
                 print("[DEBUG] main.py: Widgets principales ya existen, omitiendo creación.")

            self.root.title(f"Punto de Venta - Usuario: {self.usuario_actual['nombre']}")
            self.root.deiconify()
            print("[DEBUG] main.py: ¡INICIO COMPLETO!")

        except Exception as e:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!   ERROR FATAL EN LA INTERFAZ PRINCIPAL (post-login)   !!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            error_completo = traceback.format_exc()
            print(error_completo)
            
            messagebox.showerror("Error Crítico al Iniciar Interfaz",
                                 f"No se pudo iniciar la interfaz principal.\n\n"
                                 f"Error: {e}\n\n"
                                 f"Detalles:\n{error_completo}\n\n"
                                 f"La aplicación se cerrará.")
            self.root.destroy()

    def _crear_widgets(self):
        # --- Frames Principales ---
        header_opciones = tk.Frame(self.root, bg="#ADB2B4", height=50, bd=3, relief="ridge")
        header_opciones.pack(fill="x")

        parte_busqueda = tk.Frame(self.root, bg="#CFCFCF", height=40)
        parte_busqueda.pack(fill="x")

        body = tk.Frame(self.root, bg="#CFCFCF")
        body.pack(fill="both", expand=True)

        # --- Frame para la Grilla con Scroll ---
        contenedor_scroll = tk.Frame(self.root)
        contenedor_scroll.place(relx=0.02, rely=0.143, relwidth=0.78, relheight=0.828)
        canvas = tk.Canvas(contenedor_scroll, bg="#F5F5F5")
        scrollbar = tk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F5F5F5")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.info_articulos = scrollable_frame
        
        # --- Bloque de Totales ---
        bloque_totales = tk.Frame(body, bg="#C2DBE4", bd=1, relief="solid")
        bloque_totales.place(relx=0.81, rely=0.071, relwidth=0.16, relheight=0.143)
        tk.Label(bloque_totales, text="Subtotal:", bg="#CFCFCF", bd=1, relief="solid").place(relx=0.062, rely=0.1)
        tk.Label(bloque_totales, text="Desc/int:", bg="#CFCFCF", bd=1, relief="solid").place(relx=0.062, rely=0.4)
        tk.Label(bloque_totales, text="TOTAL:", bg="#CFCFCF", bd=1, relief="solid").place(relx=0.062, rely=0.7)
        self.valor_subt = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
        self.valor_subt.place(relx=0.625, rely=0.1)
        self.valor_desc = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
        self.valor_desc.place(relx=0.625, rely=0.4)
        self.valor_tot = tk.Label(bloque_totales, text="$0.00", bg="#CFCFCF", bd=1, relief="solid")
        self.valor_tot.place(relx=0.625, rely=0.7)

        # --- Búsqueda de Artículos ---
        self.barra_busca = tk.Entry(self.root, font=("Arial", 11))
        self.barra_busca.place(relx=0.10, rely=0.071, relwidth=0.4)
        self.lista_sugerencias = tk.Listbox(self.root, font=("Arial", 10))
        self.barra_busca.bind('<KeyRelease>', self.actualizar_sugerencias)
        self.lista_sugerencias.bind('<Double-1>', self.seleccionar_articulo_de_lista)
        self.lista_sugerencias.bind('<Return>', self.seleccionar_articulo_de_lista)
        self.root.bind('<Button-1>', lambda e: self.lista_sugerencias.place_forget() if e.widget != self.lista_sugerencias and e.widget != self.barra_busca else None)

        # --- Cantidad ---
        tk.Label(self.root, text="Cantidad:").place(relx=0.81, rely=0.071)
        self.barra_cant = tk.Entry(self.root, bd=3, relief="ridge")
        self.barra_cant.place(relx=0.87, rely=0.071, relwidth=0.1)
        self.barra_cant.insert(0, "1")

        # --- Botones del Header ---
        tk.Button(header_opciones, text="Inventario", padx=10, pady=1, font=("Inter", 8), command=self.abrir_ventana_inventario).pack(side="left", padx=5, pady=5)
        tk.Button(header_opciones, text="Ventas", padx=10, pady=1, font=("Inter", 8), command=lambda: mostrar_ultimos_tickets(self.root)).pack(side="left", padx=5, pady=5)
        
        # --- MODIFICACIÓN DE BOTÓN ---
        tk.Button(header_opciones, text="Dashboard (Gráficos)", padx=10, pady=1, font=("Inter", 8), command=lambda: abrir_ventana_graficos(self.root)).pack(side="left", padx=15, pady=5)
        # --- FIN MODIFICACIÓN ---
        
        #tk.Button(header_opciones, text="Generar Ticket Sim.", padx=10, pady=1, font=("Inter", 8), command=creartickets).pack(side="left", padx=8, pady=5)
        tk.Button(header_opciones, text="Generar PDF", padx=10, pady=1, font=("Inter", 8), command=lambda: abrir_ventana_pdf(self.root)).pack(side="left", padx=8, pady=5)
        
        # --- MEJORA 1: INICIO ---
        # Solo mostrar Proveedores y Configuración si el usuario es 'admin'
        if self.usuario_actual and self.usuario_actual.get('rol') == 'admin':
            tk.Button(header_opciones, text="Proveedores", padx=10, pady=1, font=("Inter", 8), command=lambda: abrir_ventana_proveedores(self.root)).pack(side="left", padx=8, pady=5)
        
        tk.Button(header_opciones, text="Cerrar Caja", padx=10, pady=1, bg="#ffdddd", font=("Inter", 8), command=self.gestionar_cierre_caja).pack(side="right", padx=10, pady=5)
        
        if self.usuario_actual and self.usuario_actual.get('rol') == 'admin':
            tk.Button(header_opciones, text="Configuración", padx=10, pady=1, font=("Inter", 8), command=self._abrir_ventana_usuarios).pack(side="right", padx=5, pady=5) 
        # --- MEJORA 1: FIN ---

        # --- Botones del Body ---
        tk.Label(body, text="Totales de Venta:").place(relx=0.81, rely=0.030)
        tk.Button(body, text="Cobrar", padx=10, pady=1, bg="#8CCFFF", font=("Inter", 8), bd=1, relief="solid", command=self.cobrar).place(relx=0.81, rely=0.3, relwidth=0.16, relheight=0.071)
        tk.Button(body, text="Presupuesto", command=self.calcular_presupuesto_seleccionados, padx=10, pady=1, bg="#C3C5C2", font=("Inter", 8), bd=1, relief="solid").place(relx=0.81, rely=0.8, relwidth=0.16, relheight=0.071)
        tk.Button(body, text="Nueva Venta",command=self.limpiar_resultados, padx=10, pady=1, bg="#B7E998", font=("Inter", 8), bd=1, relief="solid").place(relx=0.81, rely=0.4, relwidth=0.16, relheight=0.071)
        tk.Button(body, text="Eliminar Articulo", command=self.eliminar_articulos_seleccionados, padx=10, pady=1, bg="#F8A894", font=("Inter", 8), bd=1, relief="solid").place(relx=0.81, rely=0.5, relwidth=0.16, relheight=0.071)
        tk.Button(body, text="Aplicar Descuento", command=self.abrir_ventana_descuento, padx=10, pady=1, bg="#FDFD96", font=("Inter", 8), bd=1, relief="solid").place(relx=0.81, rely=0.6, relwidth=0.16, relheight=0.071)
        
        # --- BOTÓN "Agregar Producto" ELIMINADO ---
        # Se centraliza la lógica en la ventana "Inventario"
        
        self._mostrar_encabezados()

    def _abrir_ventana_usuarios(self):
        """Abre la ventana de gestión de usuarios."""
        print("[INFO] Click en Configuración -> Llamando a abrir_ventana_gestion_usuarios...")
        
        # Esta comprobación es una redundancia de seguridad (buena práctica)
        # por si acaso el botón estuviera visible por error.
        if self.usuario_actual and self.usuario_actual.get('rol') == 'admin':
            abrir_ventana_gestion_usuarios(self.root) 
        else:
             print("[WARN] main.py: Intento de acceso a gestión de usuarios por un no-admin.")
             messagebox.showerror("Acceso Denegado", 
                                  "Solo los usuarios con rol 'admin' pueden gestionar usuarios.", 
                                  parent=self.root)

    def cargar_lista_completa_articulos(self):
        print("[DEBUG] main.py: Cargando lista completa de artículos...")
        # La lista ahora contiene más datos (id_proveedor, nombre_proveedor)
        # pero la lógica de búsqueda principal no se ve afectada.
        try:
            articulos_db = funciones.listar_articulos()
            self.lista_articulos_completa.clear()
            self.mapa_articulos.clear()
            for art in articulos_db:
                # art[2] = descripcion, art[3] = precio
                texto_display = f"{art[2]} - ${art[3]:.2f}"
                self.lista_articulos_completa.append(texto_display)
                self.mapa_articulos[texto_display] = {"id": art[0], "codigo": art[1], "descripcion": art[2], "precio": art[3]}
            print(f"[DEBUG] main.py: {len(self.lista_articulos_completa)} artículos cargados.")
        except Exception as e:
            print(f"Error fatal al cargar lista de artículos: {e}")
            messagebox.showerror("Error Crítico", f"No se pudo cargar la lista de artículos para la venta.\n{e}")
            self.root.destroy() # Error crítico, mejor cerrar.


    def actualizar_sugerencias(self, event=None):
        texto_actual = self.barra_busca.get()
        if not texto_actual:
            self.lista_sugerencias.place_forget()
            return
        nuevos_valores = [item for item in self.lista_articulos_completa if texto_actual.lower() in item.lower()]
        if nuevos_valores:
            self.lista_sugerencias.delete(0, tk.END)
            for item in nuevos_valores:
                self.lista_sugerencias.insert(tk.END, item)
            x, y, ancho, alto = self.barra_busca.winfo_x(), self.barra_busca.winfo_y(), self.barra_busca.winfo_width(), self.barra_busca.winfo_height()
            self.lista_sugerencias.place(x=x, y=y + alto, width=ancho, height=150)
            self.lista_sugerencias.lift()
        else:
            self.lista_sugerencias.place_forget()

    def seleccionar_articulo_de_lista(self, event=None):
        if not self.lista_sugerencias.curselection():
            return
        seleccion = self.lista_sugerencias.get(self.lista_sugerencias.curselection())
        if seleccion in self.mapa_articulos:
            datos_articulo = self.mapa_articulos[seleccion]
            try:
                cantidad = int(self.barra_cant.get())
                if cantidad <= 0: raise ValueError
            except ValueError:
                cantidad = 1
                self.barra_cant.delete(0, tk.END)
                self.barra_cant.insert(0, "1")
            articulo = {
                "id": datos_articulo["id"], "codigo": datos_articulo["codigo"], "descripcion": datos_articulo["descripcion"],
                "descripcion_original": datos_articulo["descripcion"], "precio": Decimal(str(datos_articulo["precio"])),
                "precio_original": Decimal(str(datos_articulo["precio"])), "cantidad": cantidad,
                "importe": Decimal(str(datos_articulo["precio"])) * cantidad
            }
            self.articulos_agregados.append(articulo)
            self.mostrar_articulos_en_grilla()
            self.actualizar_totales()
            self.barra_busca.delete(0, tk.END)
            self.lista_sugerencias.place_forget()

    def abrir_ventana_descuento(self):
        indices_seleccionados = [i for i, var in enumerate(self.checks_articulos) if var.get()]
        if not indices_seleccionados:
            messagebox.showwarning("Sin selección", "Por favor, seleccione al menos un artículo para aplicar un descuento.")
            return
        win_desc = tk.Toplevel(self.root)
        win_desc.title("Aplicar Descuento a Selección")
        win_desc.geometry("300x150")
        win_desc.resizable(False, False)
        win_desc.transient(self.root)
        win_desc.grab_set()
        frame = ttk.Frame(win_desc, padding="15")
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Porcentaje de descuento (%):").pack(pady=5)
        entry_porcentaje = ttk.Entry(frame, justify="center")
        entry_porcentaje.pack(fill="x", pady=(0, 10))
        entry_porcentaje.focus()

        def confirmar_descuento():
            try:
                porcentaje_desc = Decimal(entry_porcentaje.get().replace(",", "."))
                if porcentaje_desc <= 0: raise ValueError("El descuento debe ser mayor a cero.")
            except (ValueError, InvalidOperation):
                messagebox.showerror("Dato inválido", "Por favor, ingrese un número válido para el porcentaje.", parent=win_desc)
                return
            for index in indices_seleccionados:
                art = self.articulos_agregados[index]
                descuento = art["precio_original"] * (porcentaje_desc / Decimal("100"))
                nuevo_precio = art["precio_original"] - descuento
                art["precio"] = nuevo_precio
                art["descripcion"] = f"{art['descripcion_original']} ({porcentaje_desc:.0f}% OFF)"
                art["importe"] = nuevo_precio * art["cantidad"]
            self.mostrar_articulos_en_grilla()
            self.actualizar_totales()
            win_desc.destroy()
        ttk.Button(frame, text="Confirmar Descuento", command=confirmar_descuento).pack(pady=15, ipady=5)

    def _ventana_apertura_caja(self):
        print("[DEBUG] main.py: INICIADA funcion _ventana_apertura_caja().")
        
        caja_existente = funciones.verificar_caja_abierta()
        if caja_existente:
            if messagebox.askyesno("Caja Abierta", "Ya existe una sesión de caja abierta. ¿Desea continuar con esa sesión?"):
                self.id_sesion_actual, self.monto_inicial_caja = caja_existente
                self.monto_inicial_caja = Decimal(str(self.monto_inicial_caja))
                self.cargar_lista_completa_articulos()
                return True 
            else:
                return False 

        apertura_exitosa = [False]

        print("[DEBUG] main.py: Creando ventana Toplevel de Apertura de Caja...")
        apertura_win = tk.Toplevel(self.root)
        apertura_win.title("Apertura de Caja")
        apertura_win.geometry("300x150")
        apertura_win.resizable(False, False)
        apertura_win.transient(self.root)
        apertura_win.grab_set() 
        tk.Label(apertura_win, text="Ingrese el monto inicial en caja:", font=("Arial", 10)).pack(pady=10)
        entry_monto = tk.Entry(apertura_win, font=("Arial", 12), justify='center')
        entry_monto.pack(pady=5, padx=20, fill='x')
        entry_monto.focus()
        print("[DEBUG] main.py: Ventana Apertura de Caja CREADA.")

        def confirmar_apertura():
            print("[DEBUG] main.py: Clic en 'Confirmar Apertura'.")
            try:
                monto_str = entry_monto.get().replace(",",".")
                monto_decimal = Decimal(monto_str)
                if monto_decimal < 0: raise ValueError("El monto no puede ser negativo")
                
                print("[DEBUG] main.py: Llamando a funciones.abrir_caja...")
                id_sesion = funciones.abrir_caja(float(monto_decimal))
                if id_sesion:
                    self.id_sesion_actual, self.monto_inicial_caja = id_sesion, monto_decimal
                    self.cargar_lista_completa_articulos()
                    apertura_exitosa[0] = True 
                    apertura_win.destroy()
                else:
                    messagebox.showerror("Error de Base de Datos", "No se pudo registrar la apertura de caja.", parent=apertura_win)
            except (ValueError, InvalidOperation) as e:
                messagebox.showerror("Dato inválido", f"Por favor, ingrese un número válido.\n{e}", parent=apertura_win)
        
        tk.Button(apertura_win, text="Confirmar", command=confirmar_apertura, bg="#B7E998").pack(pady=10)
        
        def cancelar_apertura():
             print("[DEBUG] main.py: Ventana Apertura cerrada con 'X'.")
             apertura_exitosa[0] = False
             apertura_win.destroy()
        apertura_win.protocol("WM_DELETE_WINDOW", cancelar_apertura)

        print("[DEBUG] main.py: Llamando a root.wait_window() para Apertura de Caja...")
        self.root.wait_window(apertura_win)
        
        print(f"[DEBUG] main.py: wait_window() de Apertura TERMINÓ. Devolviendo: {apertura_exitosa[0]}")
        return apertura_exitosa[0]

    def gestionar_cierre_caja(self):
        if not self.id_sesion_actual:
            messagebox.showwarning("Advertencia", "No hay una sesión de caja activa para cerrar.")
            return
        ventas = funciones.obtener_ventas_sesion(self.id_sesion_actual)
        monto_esperado = self.monto_inicial_caja + ventas.get("Efectivo", Decimal("0.0"))
        cierre_win = tk.Toplevel(self.root)
        cierre_win.title("Cierre de Caja")
        cierre_win.geometry("400x450")
        cierre_win.resizable(False, False)
        cierre_win.transient(self.root)
        cierre_win.grab_set()
        frame = tk.Frame(cierre_win, padx=15, pady=15)
        frame.pack(fill='both', expand=True)

        def crear_fila(fila, etiqueta, valor):
            tk.Label(frame, text=etiqueta).grid(row=fila, column=0, sticky='w', pady=2)
            tk.Label(frame, text=f"${valor:.2f}", font=("Arial", 10, "bold")).grid(row=fila, column=1, sticky='e', pady=2)
        tk.Label(frame, text="Resumen de Caja", font=("Arial", 14, "bold")).grid(row=0, columnspan=2, pady=10)
        crear_fila(1, "Monto Inicial:", self.monto_inicial_caja)
        crear_fila(2, "Ventas en Efectivo:", ventas.get('Efectivo', Decimal('0.0')))
        crear_fila(3, "Ventas con Tarjeta:", ventas.get('Tarjeta', Decimal('0.0')))
        crear_fila(4, "Ventas (Otros Medios):", ventas.get('Otros', Decimal('0.0')))
        ttk.Separator(frame, orient='horizontal').grid(row=5, columnspan=2, sticky='ew', pady=10)
        tk.Label(frame, text="Monto Esperado en Caja:", font=("Arial", 11, "bold")).grid(row=6, column=0, sticky='w', pady=5)
        tk.Label(frame, text=f"${monto_esperado:.2f}", font=("Arial", 11, "bold")).grid(row=6, column=1, sticky='e', pady=5)
        tk.Label(frame, text="Monto Real (Contado):", font=("Arial", 10)).grid(row=7, column=0, sticky='w', pady=10)
        entry_monto_real = tk.Entry(frame, font=("Arial", 12), justify='center')
        entry_monto_real.grid(row=7, column=1, sticky='ew')
        entry_monto_real.focus()
        label_diferencia = tk.Label(frame, text="Diferencia: $0.00", font=("Arial", 12, "bold"), fg="blue")
        label_diferencia.grid(row=8, columnspan=2, pady=10)

        def calcular_diferencia(event=None):
            try:
                monto_real_val = Decimal(entry_monto_real.get())
                diferencia = monto_real_val - monto_esperado
                color = "red" if diferencia < 0 else "green" if diferencia > 0 else "blue"
                label_diferencia.config(text=f"Diferencia: ${diferencia:.2f}", fg=color)
            except (ValueError, InvalidOperation):
                label_diferencia.config(text="Diferencia: ---", fg="black")
        entry_monto_real.bind("<KeyRelease>", calcular_diferencia)

        def confirmar_cierre():
            try:
                monto_real = Decimal(entry_monto_real.get())
                if messagebox.askyesno("Confirmar Cierre", "¿Está seguro de cerrar la caja?", parent=cierre_win):
                    funciones.cerrar_caja(self.id_sesion_actual, self.monto_inicial_caja, monto_real, ventas)
                    messagebox.showinfo("Caja Cerrada", "La aplicación se cerrará.", parent=cierre_win)
                    self.root.destroy()
            except (ValueError, InvalidOperation):
                messagebox.showerror("Dato inválido", "Ingrese un monto real válido.", parent=cierre_win)
        tk.Button(frame, text="Confirmar y Salir", command=confirmar_cierre, bg="#F8A894").grid(row=9, columnspan=2, sticky='ew', pady=15, ipady=5)

    def abrir_ventana_inventario(self):
        inventario_win = tk.Toplevel(self.root)
        inventario_win.title("Gestión de Inventario")
        inventario_win.geometry("1100x700") # Un poco más grande para el proveedor
        inventario_win.transient(self.root)
        inventario_win.grab_set()

        # --- MAPA DE PROVEEDORES (para el combobox) ---
        proveedor_map = {} # Almacena "Nombre Proveedor" -> ID
        
        # --- Frames ---
        frame_lista = tk.Frame(inventario_win, bd=2, relief="groove")
        frame_lista.pack(pady=10, padx=10, fill="both", expand=True)
        frame_controles = tk.Frame(inventario_win, bd=2, relief="groove")
        frame_controles.pack(pady=10, padx=10, fill="x")

        # --- Treeview (Grilla) ---
        columnas = ("id", "codigo", "descripcion", "precio", "stock", "proveedor")
        tree = ttk.Treeview(frame_lista, columns=columnas, show="headings")
        tree.heading("id", text="ID")
        tree.heading("codigo", text="Código")
        tree.heading("descripcion", text="Descripción")
        tree.heading("precio", text="Precio")
        tree.heading("stock", text="Stock")
        tree.heading("proveedor", text="Proveedor") # Nueva columna
        
        tree.column("id", width=50, anchor=tk.CENTER)
        tree.column("codigo", width=100, anchor=tk.CENTER)
        tree.column("descripcion", width=350)
        tree.column("precio", width=100, anchor=tk.E)
        tree.column("stock", width=100, anchor=tk.CENTER)
        tree.column("proveedor", width=200) # Nueva columna

        # --- ALERTA DE STOCK BAJO (TAGS) ---
        tree.tag_configure("low_stock", background="#FFDDDD", foreground="black") # Rojo claro
        tree.tag_configure("normal_stock", background="white", foreground="black")

        tree.pack(fill="both", expand=True)

        # --- Formulario de Controles ---
        tk.Label(frame_controles, text="Código:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_codigo = tk.Entry(frame_controles, width=30)
        entry_codigo.grid(row=0, column=1, padx=5, pady=5)
        
        entry_id = tk.Entry(frame_controles) # Campo oculto para el ID
        entry_id_proveedor = tk.Entry(frame_controles) # Campo oculto para ID Proveedor

        tk.Label(frame_controles, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_descripcion = tk.Entry(frame_controles, width=50)
        entry_descripcion.grid(row=1, column=1, padx=5, pady=5, columnspan=3)

        tk.Label(frame_controles, text="Precio:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        entry_precio = tk.Entry(frame_controles, width=20)
        entry_precio.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_controles, text="Stock:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        entry_stock = tk.Entry(frame_controles, width=20)
        entry_stock.grid(row=0, column=5, padx=5, pady=5)
        
        # --- COMBOBOX DE PROVEEDOR ---
        tk.Label(frame_controles, text="Proveedor:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        combo_proveedor = ttk.Combobox(frame_controles, state="readonly", width=47)
        combo_proveedor.grid(row=2, column=1, padx=5, pady=5, columnspan=3, sticky="w")

        # --- Cargar Proveedores en el Combobox ---
        def cargar_dropdown_proveedores():
            try:
                proveedor_map.clear()
                proveedores_db = funciones.listar_proveedores()
                nombres_proveedores = ["Sin Proveedor"] # Opción por defecto
                
                proveedor_map["Sin Proveedor"] = None # Mapear "Sin Proveedor" a None (NULL)
                
                for p in proveedores_db:
                    # p[0] = id, p[1] = nombre
                    nombres_proveedores.append(p[1])
                    proveedor_map[p[1]] = p[0]
                    
                combo_proveedor['values'] = nombres_proveedores
                combo_proveedor.set("Sin Proveedor")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los proveedores: {e}", parent=inventario_win)
        
        # --- Lógica de la ventana ---
        def cargar_articulos():
            for item in tree.get_children(): tree.delete(item)
            try:
                # listar_articulos() ahora devuelve (id, cod, desc, precio, stock, id_prov, nombre_prov)
                for art in funciones.listar_articulos():
                    stock_actual = art[4]
                    
                    # Determinar el tag de color según el stock
                    tag = "low_stock" if stock_actual <= self.LOW_STOCK_THRESHOLD else "normal_stock"
                    
                    # (art[0]...art[4]) son los datos originales, art[6] es el nombre_proveedor
                    valores_grilla = (art[0], art[1], art[2], f"{art[3]:.2f}", art[4], art[6])
                    
                    tree.insert("", tk.END, values=valores_grilla, tags=(tag,))
            except Exception as e:
                 messagebox.showerror("Error", f"No se pudieron cargar los artículos: {e}", parent=inventario_win)
        
        def limpiar_campos():
            entry_id.delete(0, tk.END)
            entry_id_proveedor.delete(0, tk.END)
            entry_codigo.delete(0, tk.END)
            entry_descripcion.delete(0, tk.END)
            entry_precio.delete(0, tk.END)
            entry_stock.delete(0, tk.END)
            combo_proveedor.set("Sin Proveedor") # Resetear combobox
            if tree.selection(): 
                tree.selection_remove(tree.selection()[0])
            entry_codigo.focus()

        def seleccionar_articulo(event):
            if not tree.selection(): return
            item = tree.item(tree.selection()[0])
            valores = item['values'] # (id, cod, desc, precio_str, stock, nombre_prov)
            
            limpiar_campos()
            entry_id.insert(0, valores[0])
            entry_codigo.insert(0, valores[1])
            entry_descripcion.insert(0, valores[2])
            entry_precio.insert(0, valores[3]) # Precio ya viene como string "$XX.XX"
            entry_stock.insert(0, valores[4])
            
            # --- Setear el combobox ---
            nombre_prov_seleccionado = valores[5]
            if nombre_prov_seleccionado in proveedor_map:
                combo_proveedor.set(nombre_prov_seleccionado)
            else:
                combo_proveedor.set("Sin Proveedor")

        tree.bind("<<TreeviewSelect>>", seleccionar_articulo)

        def guardar_articulo():
            if not all([entry_codigo.get(), entry_descripcion.get(), entry_precio.get(), entry_stock.get()]):
                messagebox.showerror("Error", "Los campos Código, Descripción, Precio y Stock son obligatorios.", parent=inventario_win)
                return
            try:
                precio = float(entry_precio.get().replace(",", ".").replace("$",""))
                stock = int(entry_stock.get())
            except ValueError:
                messagebox.showerror("Error", "Precio y Stock deben ser números válidos.", parent=inventario_win)
                return

            # --- Obtener ID del Proveedor desde el Combobox ---
            nombre_prov_seleccionado = combo_proveedor.get()
            id_proveedor_seleccionado = proveedor_map.get(nombre_prov_seleccionado, None) # Devuelve ID o None

            try:
                if entry_id.get(): # Editar
                    funciones.editar_articulo(
                        entry_id.get(), entry_codigo.get(), entry_descripcion.get(), 
                        precio, stock, id_proveedor_seleccionado
                    )
                else: # Agregar
                    funciones.agregar_articulo(
                        entry_codigo.get(), entry_descripcion.get(), 
                        precio, stock, id_proveedor_seleccionado
                    )
                
                cargar_articulos() # Recargar la grilla
                limpiar_campos()
                self.cargar_lista_completa_articulos() # Recargar la lista de búsqueda principal
                
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar el artículo:\n\n{e}", parent=inventario_win)

        def eliminar_articulo():
            if not entry_id.get():
                messagebox.showerror("Error", "Debe seleccionar un artículo para eliminar.", parent=inventario_win)
                return
            if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este artículo?", parent=inventario_win):
                try:
                    funciones.borrar_articulo(entry_id.get())
                    cargar_articulos()
                    limpiar_campos()
                    self.cargar_lista_completa_articulos() # Recargar la lista de búsqueda principal
                except Exception as e:
                    messagebox.showerror("Error al Eliminar", f"No se pudo eliminar el artículo:\n\n{e}", parent=inventario_win)

        # --- Botones del formulario ---
        tk.Button(frame_controles, text="Guardar", command=guardar_articulo, bg="#B7E998").grid(row=0, column=6, padx=10, pady=5, sticky="ew")
        tk.Button(frame_controles, text="Eliminar", command=eliminar_articulo, bg="#F8A894").grid(row=1, column=6, padx=10, pady=5, sticky="ew")
        tk.Button(frame_controles, text="Limpiar Campos", command=limpiar_campos).grid(row=2, column=6, padx=10, pady=5, sticky="ew")
        
        # --- Carga inicial ---
        cargar_dropdown_proveedores()
        cargar_articulos()
        
    # --- FIN FUNCIÓN MODIFICADA ---

    def mostrar_articulos_en_grilla(self):
        for widget in self.info_articulos.winfo_children():
            if int(widget.grid_info()["row"]) > 0: widget.destroy()
        self.checks_articulos.clear()
        for fila_num, art in enumerate(self.articulos_agregados, start=1):
            tk.Label(self.info_articulos, text=art["codigo"], font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=0, sticky="nsew")
            tk.Label(self.info_articulos, text=art["descripcion"], font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=1, sticky="nsew")
            tk.Label(self.info_articulos, text=art["cantidad"], font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=2, sticky="nsew")
            tk.Label(self.info_articulos, text=f"${art['precio']:.2f}", font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=3, sticky="nsew")
            tk.Label(self.info_articulos, text=f"${art['importe']:.2f}", font=("Arial", 11), bg="#FFFFFF", relief="solid", borderwidth=1).grid(row=fila_num, column=4, sticky="nsew")
            var_check = tk.BooleanVar()
            check = tk.Checkbutton(self.info_articulos, variable=var_check, bg="#FFFFFF")
            check.grid(row=fila_num, column=5, sticky="nsew")
            self.checks_articulos.append(var_check)
            
    def actualizar_totales(self):
        subtotal_bruto = sum(art["precio_original"] * art["cantidad"] for art in self.articulos_agregados)
        total_neto = sum(art["importe"] for art in self.articulos_agregados)
        descuento = subtotal_bruto - total_neto
        self.valor_subt.config(text=f"${subtotal_bruto:.2f}")
        self.valor_desc.config(text=f"${descuento:.2f}")
        self.valor_tot.config(text=f"${total_neto:.2f}")
        
    def _mostrar_encabezados(self):
        columnas = ["Código", "Descripción", "Cantidad", "Precio Unit.", "Importe", "Seleccionar"]
        for i, texto_col in enumerate(columnas):
            label = tk.Label(self.info_articulos, text=texto_col, bg="#96C9D9", font=("Arial", 12, "bold"), anchor="center", relief="solid", bd=1, padx=50, pady=4)
            label.grid(row=0, column=i, sticky="nsew")
            self.info_articulos.grid_columnconfigure(i, weight=1 if i != 5 else 0)

    # --- FUNCIÓN ELIMINADA ---
    # def ventana_agregar_producto(self):
    #     ... (Esta lógica ahora está integrada en abrir_ventana_inventario)

    def limpiar_resultados(self): 
        self.articulos_agregados.clear()
        self.mostrar_articulos_en_grilla()
        self.actualizar_totales()
            
    def eliminar_articulos_seleccionados(self):
        indices_a_mantener = [i for i, var in enumerate(self.checks_articulos) if not var.get()]
        self.articulos_agregados = [self.articulos_agregados[i] for i in indices_a_mantener]
        self.mostrar_articulos_en_grilla()
        self.actualizar_totales()

    def calcular_presupuesto_seleccionados(self):
        if len(self.checks_articulos) != len(self.articulos_agregados):
            messagebox.showerror("Error", "La selección no está sincronizada. Intenta agregar o eliminar artículos de nuevo."); return
        seleccionados = [art for var, art in zip(self.checks_articulos, self.articulos_agregados) if var.get()]
        if not seleccionados:
            messagebox.showinfo("Presupuesto", "No hay productos seleccionados."); return
        total_presupuesto = sum(art.get("importe", 0) for art in seleccionados)
        messagebox.showinfo("Presupuesto", f"El total de los productos seleccionados es: ${total_presupuesto:.2f}")

    def cobrar(self):
        ventana_cobro(self.root, self.articulos_agregados, self.limpiar_resultados, self.actualizar_totales, self.id_sesion_actual)

# ----- Bloque __main__ -----
if __name__ == "__main__":
    print("[DEBUG] main.py: Entrando en __name__ == __main__")
    try:
        print("[DEBUG] main.py: 1. Creando root = tk.Tk()...")
        root = tk.Tk()
        print("[DEBUG] main.py: 1. root CREADO.")
        
        print("[DEBUG] main.py: 2. Creando app = PuntoDeVentaApp(root)...")
        app = PuntoDeVentaApp(root) 
        print("[DEBUG] main.py: 2. app CREADA.")
        
        print("[DEBUG] main.py: 3. Llamando a root.mainloop()... (El programa se pausará aquí y mostrará el LoginFrame)")
        root.mainloop() 
        print("[DEBUG] main.py: 3. root.mainloop() TERMINADO. (La app se cerró).")
        
    except Exception as e:
        print(f"[ERROR] main.py: ¡¡¡ERROR FATAL en el bloque __main__!!!: {e}")
        import traceback
        traceback.print_exc()

print("[DEBUG] main.py: Fin del script.")