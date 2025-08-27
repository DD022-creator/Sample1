import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
from stego.advanced_stego import encode_data_into_image, decode_data_from_image, get_image_capacity, analyze_stego_security
from stego.image_stego import compare_images

class SteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Steganography Suite")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.carrier_image_path = tk.StringVar()
        self.output_image_path = tk.StringVar()
        self.stego_image_path = tk.StringVar()
        self.password = tk.StringVar()
        self.lsb_bits = tk.IntVar(value=1)
        self.use_compression = tk.BooleanVar(value=True)
        self.message_text = tk.StringVar()
        
        self.setup_gui()
        
    def setup_gui(self):
        # Style configuration
        style = ttk.Style()
        style.configure('TFrame', background='#2c3e50')
        style.configure('TLabel', background='#2c3e50', foreground='white', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TNotebook', background='#2c3e50')
        style.configure('TNotebook.Tab', background='#34495e', foreground='white', padding=[10, 5])
        style.map('TNotebook.Tab', background=[('selected', '#3498db')])
        
        # Main notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Encode Tab
        encode_frame = ttk.Frame(notebook, padding=10)
        decode_frame = ttk.Frame(notebook, padding=10)
        analyze_frame = ttk.Frame(notebook, padding=10)
        
        notebook.add(encode_frame, text='🔼 Encode')
        notebook.add(decode_frame, text='🔽 Decode') 
        notebook.add(analyze_frame, text='📊 Analyze')
        
        self.setup_encode_tab(encode_frame)
        self.setup_decode_tab(decode_frame)
        self.setup_analyze_tab(analyze_frame)
        
    def setup_encode_tab(self, parent):
        # Carrier Image Selection
        ttk.Label(parent, text="Carrier Image:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.carrier_image_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(parent, text="Browse", command=self.browse_carrier_image).grid(row=0, column=2)
        
        # Message Input
        ttk.Label(parent, text="Secret Message:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.message_entry = scrolledtext.ScrolledText(parent, width=50, height=5, font=('Arial', 10))
        self.message_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky='ew')
        
        # File Input Alternative
        ttk.Label(parent, text="Or select file:", font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=2)
        self.file_path = tk.StringVar()
        ttk.Entry(parent, textvariable=self.file_path, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(parent, text="Browse File", command=self.browse_file).grid(row=2, column=2)
        
        # Password
        ttk.Label(parent, text="Password:", font=('Arial', 12, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.password, show='*', width=50).grid(row=3, column=1, padx=5)
        
        # Options Frame
        options_frame = ttk.LabelFrame(parent, text="Advanced Options", padding=10)
        options_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Label(options_frame, text="LSB Bits:").grid(row=0, column=0, sticky='w')
        lsb_spinbox = ttk.Spinbox(options_frame, from_=1, to=4, textvariable=self.lsb_bits, width=5)
        lsb_spinbox.grid(row=0, column=1, padx=5)
        
        ttk.Checkbutton(options_frame, text="Use Compression", variable=self.use_compression).grid(row=0, column=2, padx=20)
        
        # Output File
        ttk.Label(parent, text="Output Image:", font=('Arial', 12, 'bold')).grid(row=5, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.output_image_path, width=50).grid(row=5, column=1, padx=5)
        ttk.Button(parent, text="Browse", command=self.browse_output_image).grid(row=5, column=2)
        
        # Capacity Info
        self.capacity_label = ttk.Label(parent, text="Capacity: Not calculated", foreground='yellow')
        self.capacity_label.grid(row=6, column=1, sticky='w', pady=2)
        
        # Encode Button
        ttk.Button(parent, text="🚀 Encode Data", command=self.encode_data, style='Accent.TButton').grid(row=7, column=1, pady=20)
        
        # Progress/Result
        self.encode_result = ttk.Label(parent, text="", foreground='green')
        self.encode_result.grid(row=8, column=1, sticky='w')
        
        # Configure grid weights
        parent.columnconfigure(1, weight=1)
        
    def setup_decode_tab(self, parent):
        # Stego Image Selection
        ttk.Label(parent, text="Stego Image:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.stego_image_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(parent, text="Browse", command=self.browse_stego_image).grid(row=0, column=2)
        
        # Password
        ttk.Label(parent, text="Password:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(parent, textvariable=self.password, show='*', width=50).grid(row=1, column=1, padx=5)
        
        # LSB Bits for decoding
        ttk.Label(parent, text="LSB Bits Used:", font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        lsb_decode = ttk.Spinbox(parent, from_=1, to=4, textvariable=self.lsb_bits, width=5)
        lsb_decode.grid(row=2, column=1, sticky='w', padx=5)
        
        # Decode Button
        ttk.Button(parent, text="🔍 Decode Data", command=self.decode_data).grid(row=3, column=1, pady=20)
        
        # Results Frame
        result_frame = ttk.LabelFrame(parent, text="Decoded Data", padding=10)
        result_frame.grid(row=4, column=0, columnspan=3, sticky='nsew', pady=10)
        
        self.decoded_text = scrolledtext.ScrolledText(result_frame, width=70, height=10, font=('Consolas', 10))
        self.decoded_text.pack(fill='both', expand=True)
        
        # Save Button
        ttk.Button(parent, text="💾 Save Decoded Data", command=self.save_decoded_data).grid(row=5, column=1, pady=10)
        
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(4, weight=1)
        
    def setup_analyze_tab(self, parent):
        # Image Selection
        ttk.Label(parent, text="Image to Analyze:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.analyze_image_path = tk.StringVar()
        ttk.Entry(parent, textvariable=self.analyze_image_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(parent, text="Browse", command=self.browse_analyze_image).grid(row=0, column=2)
        
        # Analyze Button
        ttk.Button(parent, text="🔬 Analyze Image", command=self.analyze_image).grid(row=1, column=1, pady=20)
        
        # Results Frame
        analysis_frame = ttk.LabelFrame(parent, text="Analysis Results", padding=10)
        analysis_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=10)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, width=70, height=15, font=('Consolas', 10))
        self.analysis_text.pack(fill='both', expand=True)
        
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)
    
    def browse_carrier_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.bmp")])
        if path:
            self.carrier_image_path.set(path)
            self.update_capacity_info()
    
    def browse_stego_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.bmp")])
        if path:
            self.stego_image_path.set(path)
    
    def browse_output_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            self.output_image_path.set(path)
    
    def browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_path.set(path)
    
    def browse_analyze_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.bmp")])
        if path:
            self.analyze_image_path.set(path)
    
    def update_capacity_info(self):
        if self.carrier_image_path.get() and os.path.exists(self.carrier_image_path.get()):
            try:
                capacity = get_image_capacity(self.carrier_image_path.get(), self.lsb_bits.get())
                self.capacity_label.config(text=f"Capacity: {capacity['capacity_bytes']} bytes ({capacity['capacity_kb']} KB)")
            except:
                self.capacity_label.config(text="Capacity: Error calculating")
    
    def encode_data(self):
        try:
            # Get the message data
            if self.file_path.get() and os.path.exists(self.file_path.get()):
                with open(self.file_path.get(), 'rb') as f:
                    payload = f.read()
            else:
                payload = self.message_entry.get("1.0", tk.END).strip().encode()
            
            if not payload:
                messagebox.showerror("Error", "Please enter a message or select a file")
                return
            
            if not self.password.get():
                messagebox.showerror("Error", "Please enter a password")
                return
            
            # Perform encoding
            result = encode_data_into_image(
                self.carrier_image_path.get(),
                payload,
                self.password.get(),
                self.output_image_path.get(),
                self.lsb_bits.get(),
                self.use_compression.get()
            )
            
            if result['success']:
                self.encode_result.config(text=f"✅ Success! {result['message']}\nSecurity Score: {result['security_score']:.3f}")
                messagebox.showinfo("Success", f"Encoding completed successfully!\nSecurity Score: {result['security_score']:.3f}")
            else:
                messagebox.showerror("Error", result.get('error', 'Encoding failed'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Encoding failed: {str(e)}")
    
    def decode_data(self):
        try:
            if not self.stego_image_path.get():
                messagebox.showerror("Error", "Please select a stego image")
                return
            
            if not self.password.get():
                messagebox.showerror("Error", "Please enter the password")
                return
            
            # Perform decoding
            result = decode_data_from_image(
                self.stego_image_path.get(),
                self.password.get(),
                self.lsb_bits.get()
            )
            
            if result['success']:
                # Try to decode as text first
                try:
                    decoded_text = result['data'].decode('utf-8')
                    self.decoded_text.delete("1.0", tk.END)
                    self.decoded_text.insert("1.0", decoded_text)
                    messagebox.showinfo("Success", "Message decoded successfully!")
                except UnicodeDecodeError:
                    # Show hex view for binary data
                    hex_data = result['data'].hex(' ')
                    self.decoded_text.delete("1.0", tk.END)
                    self.decoded_text.insert("1.0", f"Binary Data (hex):\n{hex_data}")
                    messagebox.showinfo("Success", "Binary data decoded successfully!")
            else:
                messagebox.showerror("Error", result.get('error', 'Decoding failed'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Decoding failed: {str(e)}")
    
    def save_decoded_data(self):
        data = self.decoded_text.get("1.0", tk.END).strip()
        if not data:
            messagebox.showerror("Error", "No data to save")
            return
        
        path = filedialog.asksaveasfilename()
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(data)
                messagebox.showinfo("Success", "Data saved successfully!")
            except:
                messagebox.showerror("Error", "Failed to save data")
    
    def analyze_image(self):
        try:
            if not self.analyze_image_path.get():
                messagebox.showerror("Error", "Please select an image to analyze")
                return
            
            # Perform security analysis
            security = analyze_stego_security(self.analyze_image_path.get())
            
            # Display results
            result_text = f"""🔒 SECURITY ANALYSIS REPORT
────────────────────────────
Security Score: {security['security_score']:.3f}/1.0
Security Level: {security['security_level']}
Detection Risk: {security['detection_risk']}

📋 RECOMMENDATION:
{security['recommendation']}

💡 INTERPRETATION:
• 0.8-1.0: Excellent stealth (very hard to detect)
• 0.6-0.8: Good stealth (hard to detect)  
• 0.4-0.6: Moderate stealth (might be detectable)
• 0.0-0.4: Poor stealth (easily detectable)
"""
            
            self.analysis_text.delete("1.0", tk.END)
            self.analysis_text.insert("1.0", result_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")

def run_gui():
    root = tk.Tk()
    app = SteganographyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()