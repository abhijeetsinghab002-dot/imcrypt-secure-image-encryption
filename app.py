import tkinter as tk
from pathlib import Path
from tkinter import filedialog,messagebox,ttk
from image_crypto import ALGORITHMS,ImageCryptoError,decrypt_image,encrypt_image

class App:
    def __init__(self,root):
        self.root=root;root.title("ImCrypt — Secure Image Encryption");root.geometry("760x560");root.configure(bg="#09101f")
        self.algorithm=tk.StringVar(value="AES-256-GCM");self.status=tk.StringVar(value="Ready. Select an operation and an image.")
        style=ttk.Style();style.theme_use("clam");style.configure("TFrame",background="#111a30");style.configure("TLabel",background="#111a30",foreground="#dce6ff",font=("Segoe UI",10));style.configure("TButton",font=("Segoe UI",10,"bold"),padding=9);style.configure("Primary.TButton",background="#655cff",foreground="white");style.configure("TEntry",fieldbackground="#080e1b",foreground="white",padding=9)
        header=tk.Frame(root,bg="#09101f");header.pack(fill="x",padx=34,pady=(28,18));tk.Label(header,text="ImCrypt",bg="#09101f",fg="white",font=("Segoe UI",28,"bold")).pack(anchor="w");tk.Label(header,text="Authenticated, lossless image encryption with a fresh random nonce.",bg="#09101f",fg="#9eadcc").pack(anchor="w")
        tabs=ttk.Notebook(root);tabs.pack(fill="both",expand=True,padx=34,pady=(0,14));enc,dec=ttk.Frame(tabs),ttk.Frame(tabs);tabs.add(enc,text="  Encrypt image  ");tabs.add(dec,text="  Decrypt image  ");self.encrypt_tab(enc);self.decrypt_tab(dec)
        tk.Label(root,textvariable=self.status,bg="#09101f",fg="#73e3ad").pack(anchor="w",padx=34,pady=(0,8));tk.Label(root,text="Keep the .key file separate and private. Losing it makes decryption impossible.",bg="#09101f",fg="#8998b8").pack(anchor="w",padx=34,pady=(0,22))
    def row(self,parent,title,variable,types):
        ttk.Label(parent,text=title).pack(anchor="w",padx=28,pady=(20,7));row=ttk.Frame(parent);row.pack(fill="x",padx=28);ttk.Entry(row,textvariable=variable).pack(side="left",fill="x",expand=True);ttk.Button(row,text="Browse",command=lambda:variable.set(filedialog.askopenfilename(filetypes=types))).pack(side="left",padx=(9,0))
    def encrypt_tab(self,tab):
        source=tk.StringVar();self.row(tab,"Image file",source,[("Images","*.png *.jpg *.jpeg *.webp *.gif *.bmp")]);ttk.Label(tab,text="Encryption algorithm").pack(anchor="w",padx=28,pady=(20,7));ttk.Combobox(tab,textvariable=self.algorithm,values=list(ALGORITHMS),state="readonly").pack(fill="x",padx=28);ttk.Button(tab,text="Encrypt image and create key",style="Primary.TButton",command=lambda:self.encrypt(source.get())).pack(fill="x",padx=28,pady=30)
    def decrypt_tab(self,tab):
        encrypted,key=tk.StringVar(),tk.StringVar();self.row(tab,"Encrypted .imc file",encrypted,[("ImCrypt files","*.imc")]);self.row(tab,"Private .key file",key,[("ImCrypt keys","*.key")]);ttk.Button(tab,text="Decrypt and restore image",style="Primary.TButton",command=lambda:self.decrypt(encrypted.get(),key.get())).pack(fill="x",padx=28,pady=30)
    def encrypt(self,source):
        if not source:return messagebox.showwarning("Select image","Please select an image first.")
        base=Path(source);output=filedialog.asksaveasfilename(defaultextension=".imc",initialfile=f"{base.stem}_encrypted.imc",filetypes=[("ImCrypt files","*.imc")])
        if not output:return
        key=filedialog.asksaveasfilename(defaultextension=".key",initialfile=f"{base.stem}.key",filetypes=[("ImCrypt keys","*.key")])
        if not key:return
        try:encrypt_image(source,output,key,self.algorithm.get());self.status.set(f"Encrypted successfully: {Path(output).name}");messagebox.showinfo("Encryption complete",f"Encrypted file:\n{output}\n\nPrivate key:\n{key}\n\nStore the key separately.")
        except ImageCryptoError as exc:messagebox.showerror("Encryption failed",str(exc))
    def decrypt(self,encrypted,key):
        if not encrypted or not key:return messagebox.showwarning("Files required","Select both the encrypted file and its private key.")
        output=filedialog.asksaveasfilename(initialfile=f"{Path(encrypted).stem}_restored")
        if not output:return
        try:restored=decrypt_image(encrypted,key,output);self.status.set(f"Restored successfully: {Path(restored).name}");messagebox.showinfo("Decryption complete",f"Original image restored exactly:\n{restored}")
        except ImageCryptoError as exc:messagebox.showerror("Decryption failed",str(exc))
if __name__=="__main__":root=tk.Tk();App(root);root.mainloop()
