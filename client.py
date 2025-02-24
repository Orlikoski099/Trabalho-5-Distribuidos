import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import tkinter as tk
from tkinter import messagebox

# Inicializando a janela principal (root) antes de qualquer widget ou variável
root = tk.Tk()
root.withdraw()  # Oculta a janela principal

# Agora é seguro criar variáveis como trip_type_var
trip_type_var = tk.StringVar()

# Definição das variáveis de entrada fora das funções
origin_entry = None
destination_entry = None
departure_date_entry = None
return_date_entry = None
num_people_entry = None
user_id_entry = None

def send_trip_request():
    trip_type = trip_type_var.get()
    origin = origin_entry.get()
    destination = destination_entry.get()
    departure_date = departure_date_entry.get()
    return_date = return_date_entry.get()
    num_people = num_people_entry.get()
    user_id = user_id_entry.get()
    
    if not origin or not destination or not departure_date or not num_people or not user_id:
        messagebox.showerror("Erro", "Todos os campos obrigatórios devem ser preenchidos!")
        return
    
    try:
        request = protocolo_pb2.TripRequest(
            trip_type=trip_type,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date if return_date else "",
            num_people=int(num_people),
            user_id=user_id,
        )
        
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = protocolo_pb2_grpc.TravelAgencyStub(channel)
            response = stub.BookTrip(request)
        
        if response.status == "Success":
            messagebox.showinfo("Sucesso", f"Reserva realizada com sucesso!\n\nDetalhes: {response.details}")
        else:
            messagebox.showerror("Erro", f"Erro na reserva: {response.status}")
    except grpc.RpcError as e:
        messagebox.showerror("Erro", f"Falha na comunicação com o servidor: {e}")

def send_cancellation_request():
    user_id = user_id_entry.get()
    if not user_id:
        messagebox.showerror("Erro", "O campo de ID de usuário deve ser preenchido!")
        return
    
    try:
        request = protocolo_pb2.CancelTripRequest(user_id=user_id)
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = protocolo_pb2_grpc.TravelAgencyStub(channel)
            response = stub.CancelBookTrip(request)
        
        if response.status == "Success":
            messagebox.showinfo("Sucesso", "Reserva excluída com sucesso!")
        else:
            messagebox.showerror("Erro", f"Erro ao excluir reserva: {response.status}")
    except grpc.RpcError as e:
        messagebox.showerror("Erro", f"Falha na comunicação com o servidor: {e}")

def show_booking_form():
    modal.title("Sistema de Viagens")
    for widget in modal.winfo_children():
        widget.destroy()

    # Inicializando os campos de entrada
    trip_type_var.set("round_trip")  # Valor padrão
    global origin_entry, destination_entry, departure_date_entry, return_date_entry, num_people_entry, user_id_entry
    origin_entry = tk.Entry(modal)
    destination_entry = tk.Entry(modal)
    departure_date_entry = tk.Entry(modal)
    return_date_entry = tk.Entry(modal)
    num_people_entry = tk.Entry(modal)
    user_id_entry = tk.Entry(modal)
    
    tk.Label(modal, text="Tipo de Viagem:").pack()
    tk.OptionMenu(modal, trip_type_var, "round_trip", "one_way").pack()
    tk.Label(modal, text="Origem:").pack()
    origin_entry.pack()
    tk.Label(modal, text="Destino:").pack()
    destination_entry.pack()
    tk.Label(modal, text="Data de Partida:").pack()
    departure_date_entry.pack()
    tk.Label(modal, text="Data de Retorno:").pack()
    return_date_entry.pack()
    tk.Label(modal, text="Número de Pessoas:").pack()
    num_people_entry.pack()
    tk.Label(modal, text="ID do Usuário:").pack()
    user_id_entry.pack()
    tk.Button(modal, text="Enviar Reserva", command=send_trip_request).pack(pady=10)

def show_cancellation_form():
    for widget in modal.winfo_children():
        widget.destroy()
    
    modal.title("Cancelamento de Viagens")
    global user_id_entry
    user_id_entry = tk.Entry(modal)

    tk.Label(modal, text="ID do Usuário:").pack()
    user_id_entry.pack()
    tk.Button(modal, text="Excluir Reserva", command=send_cancellation_request).pack(pady=10)

# Inicializando o modal corretamente
modal = tk.Toplevel(root)
modal.title("Escolha uma Ação")

tk.Button(modal, text="Fazer Nova Reserva", command=show_booking_form).pack(pady=10)
tk.Button(modal, text="Excluir Reservas", command=show_cancellation_form).pack(pady=10)

root.mainloop()
