__version__ = '2.0.0'
__author__ = 'Martin Schlüter'

import pygal
from tkinter import *
from tkinter.messagebox import showerror, askyesnocancel
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.simpledialog import askstring, askinteger

import json


class BudgetApp:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("PyBudget v2")
        self.parent.resizable(False, False)        
        parent.protocol("WM_DELETE_WINDOW", self.delete_window)
        self.number_entries = 0
        self.new_number_entries = 0

        
        # Create the menu bar
        menu = Menu(self.parent)
        
        # Create the open menu option
        menu.add_command(label="Open", command=self.open_file)
        
        # Create the new menu option
        menu.add_command(label="New", command=self.new_file)
        
        # Create the save menu option
        menu.add_command(label="Save", command=self.save_func)
        
        # Create the pie-chart menu option
        menu.add_command(label="Pie", command=self.gen_pie_chart)
        
        # Add the file submenu to the menubar
        self.parent.config(menu=menu)
        
        # Initiate Entry containers
        self.categories = {}
        self.new_categories = {}
        self.categories_budget = {}
        self.new_categories_budget = {}
        self.add_to_entry_dict = {}
        self.minus_to_entry_dict = {}
        self.remove_entry_dict = {}       
        
        self.project_name_frame = Frame(self.parent)
        self.project_name_frame.pack(side=TOP, anchor=N)
        
        self.category_frame = Frame(self.parent)
        self.category_frame.pack()        
        
        # Show the initial window.
        self.initial_window()

    def initial_window(self):
        self.initial_page = True
        intro = """Thank you for using this program!
Create or open a new project.
Warning:
- No undo button (yet?)
- Only whole numbers are supported."""
        Label(self.parent, text='Created by Martin Schlüter').pack(side=BOTTOM)
        self.intro_label = Label(self.parent, text=intro)
        self.intro_label.pack(side=BOTTOM)
       
    def open_file(self):
        self.project_name = askopenfilename(filetypes=[('Project file', '*.json')])
        if self.project_name:
            self.load_data()
        
    def new_file(self):
        self.project_name = 'placeholder'
        self.load_data()
           
    def load_data(self):
        """Function for loading the save data.""" 
        self.initial_page = False
        self.parent.focus_set()
        self.intro_label.destroy()
        self.category_frame.destroy()
        self.category_frame = Frame(self.parent)
        self.category_frame.pack()
        
        self.categories = {}
        self.categories_budget = {}
        self.new_categories = {}
        self.new_categories_budget = {}
        self.add_to_entry_dict = {}
        self.minus_to_entry_dict = {}
        self.remove_entry_dict = {}
        
        save_data = self.open_saved_project()
        
        total_label = Label(self.category_frame, text='Total (€):')
        total_label.grid(row=0, column=1)
   
        self.total = Entry(self.category_frame)
        self.total.grid(row=0, column=2)
        self.total.delete(0, END)
        self.total.insert(0, save_data['total'])
        
        category_label = Label(self.category_frame, text='Category:')
        category_budget_label = Label(self.category_frame, text='Category budget (€):')
        category_label.grid(row=1, column=1)
        category_budget_label.grid(row=1, column=2)
        
        i = 0
        for (ix, label) in enumerate(save_data['category']): 
            self.category = Entry(self.category_frame)
            self.category.grid(row=ix + 2, column=1)
            self.categories[self.number_entries] = self.category           
       
            self.category_budget = Entry(self.category_frame)
            self.category_budget.grid(row=ix + 2, column=2)
            self.categories_budget[self.number_entries] = self.category_budget
            
            # self.add_to_entry_button = Button(self.category_frame, text="+", command=lambda number=self.number_entries: self.add_to_entry_func(number))
            # self.add_to_entry_button.grid(row=ix + 2, column=3)
            # self.add_to_entry_dict[self.number_entries] = self.add_to_entry_button
            
            # self.minus_to_entry_button = Button(self.category_frame, text="-", command=lambda number=self.number_entries: self.minus_to_entry_func(number))
            # self.minus_to_entry_button.grid(row=ix + 2, column=4)
            # self.minus_to_entry_dict[self.number_entries] = self.minus_to_entry_button
            
            self.remove_entry_button = Button(self.category_frame, text="Remove", command=lambda number=self.number_entries: self.remove_entry_func(number))
            self.remove_entry_button.grid(row=ix + 2, column=3)
            self.remove_entry_dict[self.number_entries] = self.remove_entry_button
            self.number_entries += 1
            i += 1
        
        a = 0
        aa = 0
        for field in self.categories:
            self.categories[field].delete(0, END)
            self.categories[field].insert(0, save_data['category'][a])
            a += 1
            
        for field in self.categories_budget:
            self.categories_budget[field].delete(0, END)
            self.categories_budget[field].insert(0, save_data['category budget'][aa])
            aa += 1
             
        self.plus = Button(self.category_frame, text='+', command=self.new_data)
        self.plus.grid(row=self.number_entries + 3, column=3)
        
    def new_data(self):
        self.new_category = Entry(self.category_frame)
        self.new_category.grid(row=self.number_entries + self.new_number_entries + 3, column=1)
        self.new_categories[self.new_number_entries] = self.new_category
        
        self.new_category_budget = Entry(self.category_frame)
        self.new_category_budget.grid(row=self.number_entries + self.new_number_entries + 3, column=2)
        self.new_categories_budget[self.new_number_entries] = self.new_category_budget
        
        # self.add_to_entry_button = Button(self.category_frame, text="+", command=lambda number=self.number_entries: self.add_to_entry_func(number))
        # self.add_to_entry_button.grid(row=self.number_entries + self.new_number_entries + 3, column=3)
        # self.add_to_entry_dict[self.new_number_entries] = self.add_to_entry_button
        
        # self.minus_to_entry_button = Button(self.category_frame, text="-", command=lambda number=self.number_entries: self.minus_to_entry_func(number))
        # self.minus_to_entry_button.grid(row=self.number_entries + self.new_number_entries + 3, column=4)
        # self.minus_to_entry_dict[self.new_number_entries] = self.minus_to_entry_button
    
        self.remove_entry_button = Button(self.category_frame, text="Remove", command=lambda a=self.number_entries, b=self.new_number_entries: self.remove_entry_func2(a + b, b))
        self.remove_entry_button.grid(row=self.number_entries + self.new_number_entries + 3, column=3)
        self.remove_entry_dict[self.number_entries + self.new_number_entries] = self.remove_entry_button       
        
        self.new_number_entries += 1
        self.plus.destroy()
        self.plus = Button(self.category_frame, text='+', command=self.new_data)
        self.plus.grid(row=self.number_entries + self.new_number_entries + 3, column=3)
    
    # def add_to_entry_func(self, number):
        # try:      
            # var = IntVar()
            # var.set(int(self.categories_budget[number].get()) + 
                        # askinteger("Add", "How much do you want to add?") )
            # self.categories_budget[number].config(textvariable=var)
        # except TypeError:
            # pass
            
    # def minus_to_entry_func(self, number):
        # try:      
            # var = IntVar()
            # var.set(int(self.categories_budget[number].get()) + 
                        # askinteger("Subtract", "How much do you want to subtract?"))
            # self.categories_budget[number].config(textvariable=var)
        # except TypeError:
            # pass
    
    def remove_entry_func(self, number):
        self.categories[number].destroy()
        del(self.categories[number])
        self.categories_budget[number].destroy()
        del(self.categories_budget[number])
        self.remove_entry_dict[number].destroy()
        del(self.remove_entry_dict[number])
        
    def remove_entry_func2(self, number, number2):
        self.new_categories[number2].destroy()
        del(self.new_categories[number2])
        self.new_categories_budget[number2].destroy()
        del(self.new_categories_budget[number2])
        self.remove_entry_dict[number].destroy()
        del(self.remove_entry_dict[number])
    
    def delete_window(self):
        """This function is run when the X button is pressed."""
        if not self.initial_page:
            result = askyesnocancel("Exit program?", "You are about to exit the "
                     "program. Do you want to save first?")
            if result:
                self.save_func()
                self.parent.destroy()
            elif result == False:
                self.parent.destroy()
            else:
                pass
        else:
            self.parent.destroy()
        
    def save_func(self):
        """Function for saving data to a json file."""
        category1, category_budget1 = [], []
        for i in self.categories:
            if len(self.categories[i].get()) != 0:
                category1.append(self.categories[i].get())
            else:
                category1.append("Empty")
        for i in self.new_categories:
            if len(self.new_categories[i].get()) != 0:
                category1.append(self.new_categories[i].get())
            else:
                category1.append("Empty")
                
        try:      
            for i in self.categories_budget:
                if len(self.categories_budget[i].get()) != 0:
                    category_budget1.append(int(self.categories_budget[i].get()))
                else:
                    category_budget1.append(0)
            for i in self.new_categories_budget:
                if len(self.new_categories_budget[i].get()) != 0:
                    category_budget1.append(int(self.new_categories_budget[i].get()))
                else:
                    category_budget1.append(0)
            self.abort_save = False
        except ValueError:
            showerror('Error', 'Your category budget must be a number!')
            self.abort_save = True
            
        if not self.abort_save:
            try:
                save_data = {'total': int(self.total.get()), 
                             'category': category1, 
                             'category budget': category_budget1}
            except ValueError:
                showerror('Error', 'Your total can only be a number!')
            except AttributeError:
                showerror('Error', 'No file opened!')
            else:
                if sum(category_budget1) <= int(self.total.get()):
                    try:
                        self.project_name = asksaveasfilename(filetypes=[('Project file', '*.json')])
                    except TypeError:
                        pass
                    else:
                        if self.project_name.endswith('.json'):
                            with open(self.project_name, 'w') as f:
                                json.dump(save_data, f)
                        else:
                            with open(self.project_name + '.json', 'w') as f:
                                json.dump(save_data, f)
                else:
                    showerror('Error', 'You have used up too much of your budget total!')
    
    def gen_pie_chart(self):
        if not self.initial_page:
            pie_chart = pygal.Pie()
            pie_chart.title = f'{self.project_name} | total:{self.total.get()}'
            for field in self.categories:
                if len(self.categories[field].get()) != 0:
                    pie_chart.add(self.categories[field].get(), int(self.categories_budget[field].get()))
            for field in self.new_categories:
                if len(self.new_categories[field].get()) != 0:
                    pie_chart.add(self.new_categories[field].get(), int(self.new_categories_budget[field].get()))
            pie_chart.render_in_browser()
        else:
            showerror('Error', 'No file opened!')
    
    def open_saved_project(self):
        try:
            f = open(self.project_name)
        except FileNotFoundError:
            save_data = {'total': '?', 'category': ['??'], 'category budget': ['??']}
            return save_data
        else:
            save_data = json.load(f)
            f.close()
            return save_data
            
            
if __name__ == '__main__': 
    root = Tk()
    BudgetApp(root)
    root.mainloop()

