import tkinter as tk
from tkinter import ttk, messagebox
import funciones
from datetime import datetime, timedelta

# --- Importaciones de Matplotlib ---
# Necesitas tener matplotlib instalado: pip install matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)

print("[DEBUG] Iniciando interfaz_graficos.py...")

class VentanaGraficos(tk.Toplevel):
    """Ventana Toplevel para mostrar gráficos interactivos."""
    
    def __init__(self, parent):
        print("[DEBUG] interfaz_graficos: Creando VentanaGraficos...")
        super().__init__(parent)
        self.title("Dashboard de Ventas y Stock")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        # --- Mapas para los dropdowns ---
        self.articulo_map = {} # Almacena "Nombre Artículo" -> ID

        # --- Frames Principales ---
        # Frame para los filtros (controles)
        frame_controles = ttk.LabelFrame(self, text="Filtros y Controles", padding="10")
        frame_controles.pack(side="top", fill="x", padx=10, pady=10)

        # Frame para el gráfico
        frame_grafico = ttk.Frame(self, padding="10")
        frame_grafico.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

        # --- Widgets de Controles ---
        
        # --- FILA 0: TIPO DE REPORTE ---
        ttk.Label(frame_controles, text="Tipo de Reporte:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_reporte = ttk.Combobox(frame_controles, state="readonly", width=40) # Ancho ajustado
        self.combo_reporte['values'] = [
            "1. Ventas por Día (Gráfico de Línea)",
            "2. Top 10 Artículos Vendidos (Gráfico de Barras)",
            "3. Artículos en Stock por Proveedor (Gráfico de Torta)"
        ]
        self.combo_reporte.current(0)
        self.combo_reporte.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        self.combo_reporte.bind("<<ComboboxSelected>>", self._actualizar_estado_filtros)


        # --- FILA 1: FILTROS DE FECHA (FORMATO DD-MM-AAAA) ---
        # Fecha Desde
        ttk.Label(frame_controles, text="Fecha Desde:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_fecha_desde = ttk.Entry(frame_controles)
        self.entry_fecha_desde.grid(row=1, column=1, padx=5, pady=5)
        
        # Fecha Hasta
        ttk.Label(frame_controles, text="Fecha Hasta:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_fecha_hasta = ttk.Entry(frame_controles)
        self.entry_fecha_hasta.grid(row=1, column=3, padx=5, pady=5)
        
        # Texto de ayuda de formato
        ttk.Label(frame_controles, text="Formato: DD-MM-AAAA", font=("Arial", 8)).grid(row=2, column=1, padx=5, sticky="w")

        # --- FILA 3: FILTRO DE ARTÍCULO ---
        ttk.Label(frame_controles, text="Artículo:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.combo_articulo = ttk.Combobox(frame_controles, state="readonly", width=40) # Ancho ajustado
        self.combo_articulo.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="w")


        # Botón de Actualizar (movido a la derecha)
        self.btn_actualizar = ttk.Button(frame_controles, text="Actualizar Gráfico", command=self.dibujar_grafico)
        self.btn_actualizar.grid(row=0, column=4, rowspan=4, padx=20, pady=5, ipady=15, sticky="ns")

        # --- Configuración Inicial de Fechas (FORMATO DD-MM-AAAA) ---
        fecha_hoy = datetime.now()
        fecha_hace_30dias = fecha_hoy - timedelta(days=30)
        self.entry_fecha_desde.insert(0, fecha_hace_30dias.strftime("%d-%m-%Y"))
        self.entry_fecha_hasta.insert(0, fecha_hoy.strftime("%d-%m-%Y"))
        
        # --- Cargar dropdowns ---
        self._cargar_dropdown_articulos()


        # --- Preparación del Canvas de Matplotlib ---
        print("[DEBUG] interfaz_graficos: Creando canvas de Matplotlib...")
        self.figura = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figura.add_subplot(111) # 'ax' es nuestro "pincel"

        self.canvas = FigureCanvasTkAgg(self.figura, master=frame_grafico)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Barra de herramientas de Matplotlib (Zoom, Guardar, etc.)
        self.toolbar = NavigationToolbar2Tk(self.canvas, frame_grafico)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        print("[DEBUG] interfaz_graficos: Canvas creado.")

        # Dibujar el gráfico inicial y setear filtros
        self._actualizar_estado_filtros()
        self.dibujar_grafico()

    def _cargar_dropdown_articulos(self):
        """Carga la lista de artículos en el combobox de filtro."""
        try:
            self.articulo_map.clear()
            # listar_articulos() devuelve (id, cod, desc, precio, stock, id_prov, nombre_prov)
            articulos_db = funciones.listar_articulos() 
            
            nombres_articulos = ["Todos los Artículos"] # Opción por defecto
            self.articulo_map["Todos los Artículos"] = None # Mapear a None
            
            for art in articulos_db:
                # art[0] = id, art[2] = descripcion
                nombres_articulos.append(art[2])
                self.articulo_map[art[2]] = art[0]
                
            self.combo_articulo['values'] = nombres_articulos
            self.combo_articulo.set("Todos los Artículos")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los artículos: {e}", parent=self)

    def _validar_fechas(self):
        """Valida las fechas de los Entry. Devuelve (fecha_desde, fecha_hasta) o None."""
        try:
            f_desde_str = self.entry_fecha_desde.get()
            f_hasta_str = self.entry_fecha_hasta.get()
            
            # --- VALIDACIÓN CAMBIADA A DD-MM-AAAA ---
            f_desde = datetime.strptime(f_desde_str, "%d-%m-%Y").date()
            f_hasta = datetime.strptime(f_hasta_str, "%d-%m-%Y").date()
            
            if f_hasta < f_desde:
                 messagebox.showerror("Error de Fechas", "La 'Fecha Hasta' no puede ser anterior a la 'Fecha Desde'.", parent=self)
                 return None, None
                 
            return f_desde, f_hasta
        except ValueError:
            messagebox.showerror("Error de Formato", "Por favor, ingrese las fechas en formato DD-MM-AAAA.", parent=self)
            return None, None
            
    def _actualizar_estado_filtros(self, event=None):
        """Activa o desactiva los filtros de fecha y artículo según el reporte."""
        reporte_seleccionado = self.combo_reporte.get()
        
        # Reporte 1 (Ventas por Día): Usa Fecha y Artículo
        if reporte_seleccionado.startswith("1."):
            self.entry_fecha_desde.config(state="normal")
            self.entry_fecha_hasta.config(state="normal")
            self.combo_articulo.config(state="readonly")
            
        # Reporte 2 (Top 10): Solo usa Fecha
        elif reporte_seleccionado.startswith("2."):
            self.entry_fecha_desde.config(state="normal")
            self.entry_fecha_hasta.config(state="normal")
            self.combo_articulo.config(state="disabled")
            
        # Reporte 3 (Stock por Proveedor): No usa filtros
        elif reporte_seleccionado.startswith("3."):
            self.entry_fecha_desde.config(state="disabled")
            self.entry_fecha_hasta.config(state="disabled")
            self.combo_articulo.config(state="disabled")


    def dibujar_grafico(self):
        """Función principal que decide qué gráfico dibujar."""
        print("[DEBUG] interfaz_graficos: Llamando a dibujar_grafico()...")
        reporte_seleccionado = self.combo_reporte.get()
        
        # Limpiar el gráfico anterior
        self.ax.clear() 
        
        try:
            if reporte_seleccionado.startswith("1."):
                # --- Reporte 1: Ventas por Día (Línea) ---
                f_desde, f_hasta = self._validar_fechas()
                if f_desde is None: return
                
                # --- Nuevo: Obtener ID del artículo seleccionado ---
                nombre_articulo_sel = self.combo_articulo.get()
                id_articulo_sel = self.articulo_map.get(nombre_articulo_sel, None)
                
                # --- Pasar el id_articulo a la función de backend ---
                datos = funciones.get_ventas_por_dia(f_desde, f_hasta, id_articulo_sel)
                
                if not datos:
                    self.ax.text(0.5, 0.5, "No hay datos de ventas para esta selección.", horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
                else:
                    fechas = [fila.fecha_dia for fila in datos]
                    totales = [float(fila.total_dia) for fila in datos] # Convertir Decimal
                    
                    self.ax.plot(fechas, totales, marker='o', linestyle='-', color='green')
                    titulo = f"Ventas Diarias ({f_desde.strftime('%d/%m/%Y')} a {f_hasta.strftime('%d/%m/%Y')})"
                    if id_articulo_sel:
                        titulo += f"\nArtículo: {nombre_articulo_sel}"
                    self.ax.set_title(titulo)
                    self.ax.set_xlabel("Fecha")
                    self.ax.set_ylabel("Total Vendido ($)")
                    self.figura.autofmt_xdate() # Rota las fechas para que se lean bien
            
            elif reporte_seleccionado.startswith("2."):
                # --- Reporte 2: Top 10 Artículos (Barras) ---
                f_desde, f_hasta = self._validar_fechas()
                if f_desde is None: return
                
                datos = funciones.get_top_articulos_vendidos(f_desde, f_hasta, top_n=10)
                if not datos:
                    self.ax.text(0.5, 0.5, "No hay artículos vendidos en este rango.", horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
                else:
                    # Datos vienen ordenados (DESC)
                    nombres = [fila[0] for fila in datos]
                    totales = [float(fila[1]) for fila in datos]
                    
                    # Invertir para que el más alto quede arriba en el barh
                    nombres.reverse()
                    totales.reverse()
                    
                    self.ax.barh(nombres, totales, color='skyblue')
                    self.ax.set_title(f"Top 10 Artículos Vendidos ({f_desde.strftime('%d/%m/%Y')} a {f_hasta.strftime('%d/%m/%Y')})")
                    self.ax.set_xlabel("Total Vendido ($)")
                    
            elif reporte_seleccionado.startswith("3."):
                # --- Reporte 3: Stock por Proveedor (Torta) ---
                datos = funciones.get_stock_por_proveedor()
                if not datos:
                    self.ax.text(0.5, 0.5, "No hay artículos o proveedores cargados.", horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
                else:
                    nombres = [fila[0] for fila in datos]
                    cantidades = [fila[1] for fila in datos]
                    
                    self.ax.pie(cantidades, labels=nombres, autopct='%1.1f%%', startangle=140)
                    self.ax.set_title("Artículos en Stock por Proveedor")
                    self.ax.axis('equal') # Asegura que la torta sea circular

            # --- Actualizar el Canvas ---
            self.ax.grid(True, linestyle='--', alpha=0.6) # Añadir una grilla suave
            self.figura.tight_layout() # Ajusta el gráfico para que no se corten las etiquetas
            self.canvas.draw()
            print("[DEBUG] interfaz_graficos: Gráfico dibujado/actualizado.")
            
        except Exception as e:
            print(f"[ERROR] interfaz_graficos: Error al dibujar gráfico: {e}")
            messagebox.showerror("Error de Gráfico", f"No se pudo generar el gráfico:\n{e}", parent=self)

# --- Función de conveniencia para abrir la ventana ---
def abrir_ventana_graficos(parent):
    VentanaGraficos(parent)

print("[DEBUG] interfaz_graficos.py: Archivo importado.")