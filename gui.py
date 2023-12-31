from PyPDF2 import PdfMerger
import glob
import os
from datetime import datetime
from PyPDF2 import PdfMerger
from customtkinter import *

set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
set_default_color_theme("dark-blue")

pointy = {'corner_radius': 0}  # To remove round corners


class App(CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PDF Merger")
        self.geometry("900x420")
        self.resizable(False, False)


class MainFrame(CTkFrame):
    def __init__(self, container) -> None:
        super().__init__(container, **pointy, fg_color='transparent')
        self.folder_path = ''
        self.pack()

        frm_search_folder = CTkFrame(self, **pointy)
        frm_search_folder.pack(padx=10, pady=(30, 10))

        lbl_folder_path = CTkLabel(frm_search_folder, text="Folder Path", font=CTkFont(size=15, family="monospace"))
        lbl_folder_path.grid(row=0, column=0, padx=(10, 20))

        btn_toggle_appearance = CTkButton(frm_search_folder, text="Dark/Light", font=CTkFont(size=15, family="monospace"), width=80, **pointy, command=lambda: self.toggle_appearance())
        btn_toggle_appearance.grid(row=1, column=0, padx=(10, 0), sticky='nw')

        ent_folder_path = CTkEntry(frm_search_folder, placeholder_text='Enter folder path or load folder', font=CTkFont(size=13, family="monospace"), width=480, **pointy)
        ent_folder_path.grid(row=0, column=1, padx=(0, 20))

        btn_merge = CTkButton(frm_search_folder, text="Merge", font=CTkFont(size=15, family="monospace"), width=120, **pointy, command=lambda: self.display_merged(scl_display))
        btn_merge.grid(row=1, column=1, sticky='n')

        btn_search = CTkButton(frm_search_folder, text="Search", font=CTkFont(size=15, family="monospace"), width=150, **pointy, command=lambda: self.search_folder(ent_folder_path))
        btn_search.grid(row=0, column=2, padx=(0, 10), pady=(5, 5), sticky='e')

        btn_load_folder = CTkButton(frm_search_folder, text="Load", font=CTkFont(size=15, family="monospace"), width=150, **pointy, command=lambda: self.load_folder(ent_folder_path))
        btn_load_folder.grid(row=1, column=2, padx=(0, 10), pady=(0, 5), sticky='e')

        frm_display_folders = CTkFrame(self, **pointy, width=700)
        frm_display_folders.pack(pady=(0, 20))

        scl_display = CTkScrollableFrame(frm_display_folders, width=800, height=250, **pointy)
        scl_display.pack()

        btn_clear = CTkButton(frm_display_folders, text="Clear All", **pointy, command=lambda: self.clear_display(scl_display))
        btn_clear.pack(fill="x")

    @staticmethod
    def toggle_appearance() -> None:
        current = get_appearance_mode()

        if current == "Light":
            set_appearance_mode("Dark")
            return
        
        set_appearance_mode("Light")

    def search_folder(self, ent_folder_path) -> None:
        self.folder_path = ent_folder_path.get()
    
    def load_folder(self, ent_folder_path) -> None:
        self.folder_path = filedialog.askdirectory()

        if not self.folder_path:
            return

        if ent_folder_path:
            ent_folder_path.delete(1, END)
        
        ent_folder_path.insert(END, self.folder_path)

    @staticmethod
    def clear_display(scl_display) -> None:
        for element in scl_display.winfo_children():
            element.destroy()

    def display_merged(self, scl_display) -> None:
        self.clear_display(scl_display)

        if not self.folder_path: return

        if not self.folder_path.endswith(os.path.sep):
            self.folder_path += os.path.sep
        
        now = datetime.now()
    
        file_path = f"{self.folder_path} {now.strftime('%Y-%m-%d_%H%M%S')} merge details.txt"

        roots_not_empty = self.scan_folders()

        if roots_not_empty:
            file = open(file_path, 'a', encoding='utf-8')
            count = 0

            for folder in roots_not_empty:
                str_path = os.path.join(folder, '*.pdf')  # Use os.path.join for paths

                print(f"Merging files in {folder}...")

                files = glob.glob(str_path, recursive=True)

                number_of_pages = self.merge_pdf(files, os.path.join(folder, 'output.pdf'))

                if number_of_pages > 0:
                    lbl_path = CTkLabel(scl_display, text=f"📁 {folder}")
                    lbl_pages = CTkLabel(scl_display, text=f"=> {number_of_pages} pages")

                    lbl_path.grid(row=count, column=0, padx=5, pady=(5, 0), sticky='w')
                    lbl_pages.grid(row=count, column=1, sticky='e')

                    count += 1

                    file.write(f"📁 {folder} => {number_of_pages} pages" + "\n")
                    print(f"📄 Merged files in {folder}" + "\n")

                else:
                    file.write(f"No merging done for {folder}" + "\n")
                    print(f"No merging done for {folder}" + "\n")

            if count == 0:
                lbl_no_files = CTkLabel(scl_display, text='No files to merge...')
                lbl_no_files.grid(row=count, column=0, padx=5,  pady=(5, 0), sticky='w')
                    
            file.close()

    def scan_folders(self):
        list_roots = []
        
        for (root, dirs, files) in os.walk(self.folder_path, topdown=True):
            if any(f.endswith('.pdf') for f in files):
                list_roots.append(root)
        
        return list_roots

    def merge_pdf(self, files, filename):
        if len(files) == 1:  # If there's only one PDF file, skip merging
            print(f"Skipping merge for {filename} as there's only one PDF file.")
            return 0

        merger = PdfMerger()
        for pdf_file in files:
            merger.append(pdf_file)
            
            # merger.append(i)
        merger.write(filename)
        num_pages = len(merger.pages)
        merger.close()
        return num_pages


def main() -> None:
    app = App()
    main = MainFrame(app)
    app.mainloop()


if __name__ == "__main__":
    main()