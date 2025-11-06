import tkinter as tk
from tkinter import ttk, messagebox 
from funciones import verificar_usuario, agregar_usuario 

print("[DEBUG] Iniciando interfaz_login.py (V3.2 - Registro)...")

class LoginFrame(ttk.Frame): 
    """Un Frame (ahora ttk.Frame) que contiene los widgets de login."""
    def __init__(self, master, on_success, on_cancel, **kwargs):
        print("[DEBUG] LoginFrame.__init__ INICIADO.")
        super().__init__(master, padding="20", **kwargs) 
        self.master = master
        self.on_success = on_success
        self.on_cancel = on_cancel
        
        self.master.title("Inicio de Sesión - Punto de Venta")

        self.master.geometry("350x240")
        self.master.resizable(False, False)
        self.master.eval('tk::PlaceWindow . center')

        self._crear_widgets()
        print("[DEBUG] LoginFrame.__init__ TERMINADO.")

    def _abrir_ventana_registro(self):
        """Crea y muestra la ventana Toplevel para el registro de usuarios."""
        
        ventana = tk.Toplevel(self.master)
        ventana.title("Registro de Nuevo Usuario")
        ventana.geometry("350x300")
        ventana.resizable(False, False)
        ventana.transient(self.master) # Mantener por encima de la principal
        ventana.grab_set() # Modal: bloquear interacción con login

        frame = ttk.Frame(ventana, padding="20")
        frame.pack(fill="both", expand=True)

        # --- Campos del formulario ---
        ttk.Label(frame, text="Username:*").pack(anchor="w")
        e_user = ttk.Entry(frame)
        e_user.pack(fill="x", pady=(0, 10))
        e_user.focus()

        ttk.Label(frame, text="Nombre Completo (Opcional):").pack(anchor="w")
        e_nombre = ttk.Entry(frame)
        e_nombre.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Contraseña:*").pack(anchor="w")
        e_pass1 = ttk.Entry(frame, show="*")
        e_pass1.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Confirmar Contraseña:*").pack(anchor="w")
        e_pass2 = ttk.Entry(frame, show="*")
        e_pass2.pack(fill="x", pady=(0, 10))

        # --- Función de confirmación anidada ---
        def _confirmar_registro():
            username = e_user.get().strip()
            nombre = e_nombre.get().strip() or None # Permitir NULL
            pass1 = e_pass1.get()
            pass2 = e_pass2.get()
            
            # Rol Fijo por seguridad
            rol = 'vendedor' 
            
            # --- Validaciones ---
            if not all([username, pass1, pass2]):
                messagebox.showerror("Error", "Username y ambos campos de contraseña son obligatorios.", parent=ventana)
                return
            
            if pass1 != pass2:
                messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=ventana)
                return
            
            # --- Llamada al Backend ---
            try:
                # Usamos la función de 'funciones.py'
                agregar_usuario(username, nombre, rol, pass1)
                
                messagebox.showinfo("Éxito", 
                                    f"¡Usuario '{username}' registrado exitosamente!\n"
                                    "Rol asignado: 'vendedor'.\n\n"
                                    "Ahora puede iniciar sesión.", 
                                    parent=ventana)
                ventana.destroy()
                
            except Exception as e:
                # Capturamos errores (ej. "username ya existe")
                messagebox.showerror("Error de Registro", f"{e}", parent=ventana)
        
        # --- Botón de confirmación ---
        btn_confirmar = ttk.Button(frame, text="Confirmar Registro", command=_confirmar_registro)
        btn_confirmar.pack(pady=10, fill="x", ipady=4)
        
        # Permitir presionar Enter para confirmar
        ventana.bind('<Return>', lambda event: _confirmar_registro())

    def _crear_widgets(self):
        print("[DEBUG] LoginFrame._crear_widgets INICIADO.")
        
        ttk.Label(self, text="Usuario:", font=("Arial", 10)).pack(pady=5)
        self.entry_usuario = ttk.Entry(self, font=("Arial", 10))
        self.entry_usuario.pack(fill="x", pady=5)
        self.entry_usuario.focus()

        ttk.Label(self, text="Contraseña:", font=("Arial", 10)).pack(pady=5)
        self.entry_pass = ttk.Entry(self, show="*", font=("Arial", 10))
        self.entry_pass.pack(fill="x", pady=5)

        # Frame para botones (puede ser ttk también)
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(10, 0)) # Aumentado el padding superior

        style = ttk.Style(self)
        style.configure("Login.TButton", font=("Arial", 10), padding=(0, 3)) # Padding vertical
        
        # --- Botones actualizados ---
        btn_ingresar = ttk.Button(button_frame, text="Ingresar", style="Login.TButton", command=self.intentar_login)
        btn_ingresar.pack(side="left", expand=True, fill="x", padx=(0, 3))
        
        btn_registrar = ttk.Button(button_frame, text="Registrarse", style="Login.TButton", command=self._abrir_ventana_registro)
        btn_registrar.pack(side="left", expand=True, fill="x", padx=3)
        
        btn_cancelar = ttk.Button(button_frame, text="Cancelar", style="Login.TButton", command=self.on_cancel) 
        btn_cancelar.pack(side="left", expand=True, fill="x", padx=(3, 0))

        self.master.bind('<Return>', lambda event: self.intentar_login())
        self.master.protocol("WM_DELETE_WINDOW", self.on_cancel) 
        print("[DEBUG] LoginFrame._crear_widgets TERMINADO.")

    def intentar_login(self):
        print("[DEBUG] LoginFrame: Clic en 'Ingresar'.")
        username = self.entry_usuario.get()
        password = self.entry_pass.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Debe ingresar usuario y contraseña.", parent=self.master)
            return

        print("[DEBUG] LoginFrame: Llamando a funciones.verificar_usuario...")
        usuario_info = verificar_usuario(username, password)
        print(f"[DEBUG] LoginFrame: verificar_usuario devolvió: {usuario_info}")
        
        if usuario_info:
            self.on_success(usuario_info) 
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.", parent=self.master)
            self.entry_pass.delete(0, tk.END)

print("[DEBUG] interfaz_login.py (V3.2): Archivo importado.")