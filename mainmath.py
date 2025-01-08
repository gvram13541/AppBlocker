import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx


class Graph:
    def __init__(self):
        self.graph = nx.Graph()

    def add_edge(self, u, v):
        self.graph.add_edge(u, v)

    def delete_edge(self, u, v):
        self.graph.remove_edge(u, v)

    def reset_graph(self):
        self.graph.clear()

    def is_eulerian(self):
        for vertex in self.graph.nodes:
            if self.graph.degree(vertex) % 2 != 0:
                return False
        return True

    def find_cycles(self, u, visited, stack, parent, cycles):
        visited[u] = True
        stack.append(u)

        for neighbor in self.graph.neighbors(u):
            if not visited[neighbor]:
                self.find_cycles(neighbor, visited, stack, u, cycles)
            elif neighbor != parent and neighbor in stack:
                cycle_start = stack.index(neighbor)
                cycles.append(stack[cycle_start:] + [
                    neighbor])

        stack.pop()

    def check_cycles_through_vertex(self, v):
        visited = {vertex: False for vertex in self.graph.nodes}
        cycles = []
        for vertex in self.graph.nodes:
            if not visited[vertex]:
                self.find_cycles(vertex, visited, [], -1, cycles)

        for cycle in cycles:
            if v not in cycle:
                return False
        return True

    def is_arbitrarily_traceable(self, v):
        if not self.is_eulerian():
            return False
        return self.check_cycles_through_vertex(v)


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.graph = Graph()

        self.root.title("Graph Arbitrary Traceability Checker")
        self.root.geometry("800x600")

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12), padding=5)
        self.style.configure("TButton", font=("Arial", 12), padding=5)
        self.style.configure("TEntry", font=("Arial", 12), padding=5)

        self.init_ui()

    def init_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.place(relx=0.5, rely=0.2, anchor="center")

        ttk.Label(main_frame, text="Add Edge (u, v):").grid(row=0, column=0, padx=10, pady=10)

        self.u_entry = ttk.Entry(main_frame)
        self.u_entry.grid(row=0, column=1, padx=10)
        self.u_entry.bind("<Return>", lambda e: self.v_entry.focus())  

        self.v_entry = ttk.Entry(main_frame)
        self.v_entry.grid(row=0, column=2, padx=10)
        self.v_entry.bind("<Return>", lambda e: self.add_edge_and_reset_focus())  
        self.v_entry.bind("<Shift-Return>", lambda e: self.add_edge_and_reset_focus())  
        
        add_edge_button = ttk.Button(main_frame, text="Add Edge", command=self.add_edge_and_reset_focus)
        add_edge_button.grid(row=0, column=3, padx=10)

        ttk.Label(main_frame, text="Delete Edge (u, v):").grid(row=1, column=0, padx=10, pady=10)

        self.del_u_entry = ttk.Entry(main_frame)
        self.del_u_entry.grid(row=1, column=1, padx=10)
        self.del_u_entry.bind("<Return>", lambda e: self.del_v_entry.focus())  

        self.del_v_entry = ttk.Entry(main_frame)
        self.del_v_entry.grid(row=1, column=2, padx=10)
        self.del_v_entry.bind("<Return>", lambda e: self.delete_edge())  

        delete_edge_button = ttk.Button(main_frame, text="Delete Edge", command=self.delete_edge)
        delete_edge_button.grid(row=1, column=3, padx=10)

        ttk.Label(main_frame, text="Check Arbitrary Traceability from Vertex:").grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.check_vertex_entry = ttk.Entry(main_frame)
        self.check_vertex_entry.grid(row=2, column=2, padx=10)
        self.check_vertex_entry.bind("<Return>", lambda e: check_button.focus())  

        check_button = ttk.Button(main_frame, text="Check", command=self.check_arbitrary_traceability)
        check_button.grid(row=2, column=3, padx=10)

        reset_button = ttk.Button(main_frame, text="Reset Graph", command=self.reset_graph)
        reset_button.grid(row=3, column=0, columnspan=4, pady=10)

        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 12, "italic"), foreground="blue")
        self.result_label.grid(row=4, column=0, columnspan=4, pady=10)

        self.figure = Figure(figsize=(15, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis("off")
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().place(relx=0.5, rely=0.7, anchor="center")

    def add_edge_and_reset_focus(self):
        self.add_edge()
        self.u_entry.focus()  
        self.u_entry.delete(0, tk.END)  
        self.v_entry.delete(0, tk.END)  


    def add_edge(self):
        try:
            u = int(self.u_entry.get())
            v = int(self.v_entry.get())

            self.graph.add_edge(u, v)
            self.u_entry.delete(0, tk.END)
            self.v_entry.delete(0, tk.END)

            self.update_graph()
            messagebox.showinfo("Success", f"Edge ({u}, {v}) added successfully.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer vertices.")

    def delete_edge(self):
        try:
            u = int(self.del_u_entry.get())
            v = int(self.del_v_entry.get())

            self.graph.delete_edge(u, v)
            self.del_u_entry.delete(0, tk.END)
            self.del_v_entry.delete(0, tk.END)

            self.update_graph()
            messagebox.showinfo("Success", f"Edge ({u}, {v}) deleted successfully.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer vertices.")
        except nx.NetworkXError:
            messagebox.showerror("Error", "Edge does not exist.")

    def reset_graph(self):
        self.graph.reset_graph()
        self.update_graph()
        messagebox.showinfo("Success", "Graph has been reset.")

    def update_graph(self):
        self.ax.clear()
        self.ax.axis("off")
        pos = nx.spring_layout(self.graph.graph) 
        nx.draw(
            self.graph.graph,
            pos,
            ax=self.ax,
            with_labels=True,
            node_color="lightblue",
            edge_color="gray",
            node_size=500,
            font_size=10,
        )
        self.canvas.draw()  
    def check_arbitrary_traceability(self):
        try:
            vertex = int(self.check_vertex_entry.get())
            if self.graph.is_arbitrarily_traceable(vertex):
                self.result_label.config(text=f"The graph is arbitrarily traceable from vertex {vertex}.", foreground="green")
            else:
                self.result_label.config(text=f"The graph is not arbitrarily traceable from vertex {vertex}.", foreground="red")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer vertex.")
        except KeyError:
            messagebox.showerror("Error", f"Vertex {vertex} is not in the graph.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
