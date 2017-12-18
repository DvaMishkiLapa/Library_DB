from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
import fileinput

from db import DBManager

class DBViewer:
    def __init__(self, master):
        # Main window
        self.master = master
        self.master.title('Library DB')
        self.master.minsize(width=1024, height=768)

        menubar = Menu(self.master)

        menu = Menu(self.master, tearoff=0)
        menu.add_command(label='Записать изменения', command=self.save_changes)
        menu.add_command(label='Удалить изменения', command=self.rm_changes)
        menubar.add_cascade(label='База данных', menu=menu)

        self.master.config(menu=menubar)

        tree_frame = ttk.Frame(self.master)
        sql_buttons_frame1 = ttk.Frame(self.master)
        sql_buttons_frame2 = ttk.Frame(self.master)
        sql_buttons_frame3 = ttk.Frame(self.master)
        btns_frame = ttk.Frame(self.master)

        # Combobox with select of table
        self.combo = ttk.Combobox(btns_frame)
        self.combo.bind('<<ComboboxSelected>>', self.cmb_update)

        self.tree = ttk.Treeview(tree_frame, selectmode='extended')
        tree_x_scroll = ttk.Scrollbar(tree_frame, orient='hor', command=self.tree.xview)
        tree_y_scroll = ttk.Scrollbar(tree_frame, orient='vert', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_y_scroll.set)
        self.tree.configure(xscrollcommand=tree_x_scroll.set)

        tree_y_scroll.pack(side='right', fill='y')
        self.tree.pack(side='top', fill='both', expand=True)
        tree_x_scroll.pack(side='bottom', fill='x')

        # Entry
        self.entry = ttk.Entry(btns_frame)

        # Buttons
        book_by_name = ttk.Button(sql_buttons_frame1, text='Поиск книги по названию', command=lambda: True)
        book_by_author = ttk.Button(sql_buttons_frame1, text='Поиск книги по автору', command=lambda: True)
        book_by_date = ttk.Button(sql_buttons_frame1, text='Поиск книги дате', command=lambda: True)
        book_by_id = ttk.Button(sql_buttons_frame1, text='Поиск книги по ID', command=lambda: True)
        canTake = ttk.Button(sql_buttons_frame1, text='Свободные книги', command=lambda: True)

        sql_btn = ttk.Button(btns_frame, text='Выполнить SQL', command=self.run_sql)

        # Packs all elements
        tree_frame.pack(side='top', fill='both', expand=False)

        btns_frame.pack(side='bottom', fill='both')

        sql_buttons_frame1.pack(side='bottom', fill='both', padx=5, pady=10)

        self.combo.pack(side='left', padx=5, pady=5)
        self.entry.pack(side='right', padx=5, pady=5)

        book_by_name.pack(side='left', padx=5, pady=5)
        book_by_author.pack(side='left', padx=5, pady=5)
        book_by_date.pack(side='left', padx=5, pady=5)
        book_by_id.pack(side='left', padx=5, pady=5)
        canTake.pack(side='left', padx=5, pady=5)

        sql_btn.pack(side='right', padx=5, pady=5)


        self.filename = 'lib.db'
        self.start()

    def tree_update(self, cursor, columns):
        db = DBManager(self.filename)
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.tree['show'] = 'headings'
        self.tree['columns'] = ()
        self.tree['columns'] = tuple(columns)
        for col in columns:
            self.tree.column(col, stretch=False, width=100)
            self.tree.heading(col, text=col)

        for row in cursor:
            self.tree.insert('', 'end', values=row)

    def get_item_values(self, item):
        for child in self.tree.get_children():
            if child == item:
                return self.tree.item(child)["values"]

    def start(self):
        db = DBManager(self.filename)
        self.combo['values'] = ()
        for row in db.get_tables_names():
            self.combo['values'] += row
        self.combo.current(0)
        cols = db.get_columns_names(self.combo.get())
        curs = db.get_rows(self.combo.get())
        self.tree_update(curs, cols)


    def save_changes(self):
        db = DBManager(self.filename)
        table = self.combo.get()
        db.query("DELETE FROM {}".format(table))
        cols = str(self.tree['columns'])[1:-1]
        columns = "(" + cols + ")"
        values = ''
        for i in self.tree.get_children():
            vals = str(self.tree.item(i)['values'])[1:-1]
            values += "(" + vals + "), "
        query = "INSERT INTO {} {} VALUES {}".format(table, columns, values[:-2])
        db.query(query)


    # def add_row(self):
    #     self.add_window = Toplevel(self.master)
    #     self.add_window.grab_set()
    #     self.add_window.title('Добавить запись')
    #     height = 48

    #     db = DBManager(self.filename)
    #     cols = db.get_columns_names(self.combo.get())
    #     for col in cols:
    #         label = ttk.Label(self.add_window, text=col)
    #         label.pack(side="top", fill="both", padx=5, pady=5)
    #         entry = ttk.Entry(self.add_window)
    #         entry.pack(side="top", fill="both", padx=5, pady=5)
    #         height += 48
    #     self.add_window.minsize(320, height)
    #     self.add_window.resizable(0, 0)
    #     ok = ttk.Button(self.add_window, text='Ок', command=self.go_add_row)
    #     cancel = ttk.Button(self.add_window, text='Отмена', command=self.add_window.destroy)
    #     cancel.pack(side="right", padx=5, pady=5)
    #     ok.pack(side="right", padx=5, pady=5)

    def rm_changes(self):
        self.start()

    def cmb_update(self, _event):
        db = DBManager(self.filename)
        cols = db.get_columns_names(self.combo.get())
        curs = db.get_rows(self.combo.get())
        self.tree_update(curs, cols)

    def run_sql(self):
        query = self.entry.get()
        db = DBManager(self.filename)
        try:
            curs = db.query(query)
            cols = list(map(lambda x: x[0], curs.description))
            self.tree_update(curs, cols)
        except Exception as e:
            self.error_window = Toplevel(self.master)
            self.error_window.grab_set()
            self.error_window.title('Что-то пошло не так :(')
            self.error_window.minsize(320, 48)
            self.error_window.resizable(0, 0)
            label = ttk.Label(self.error_window, text=e)
            label.pack(side="top", fill="both", padx=5, pady=5)
            ok = ttk.Button(self.error_window, text='Ок', command=self.error_window.destroy)
            ok.pack(side="right", padx=5, pady=5)

root = Tk()
db_viewer = DBViewer(root)
root.mainloop()
