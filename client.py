import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import tkinter as tk
from tkinter import messagebox

# Função para enviar a solicitação de reserva de viagem ao servidor gRPC
def send_trip_request():
    # Coleta os dados dos campos
    trip_type = trip_type_var.get()
    origin = origin_entry.get()
    destination = destination_entry.get()
    departure_date = departure_date_entry.get()
    return_date = return_date_entry.get()
    num_people = num_people_entry.get()

    # Validação de dados
    if not origin or not destination or not departure_date or not num_people:
        messagebox.showerror("Erro", "Todos os campos obrigatórios devem ser preenchidos!")
        return

    try:
        request = protocolo_pb2.TripRequest(
            trip_type=trip_type,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date if return_date else "",
            num_people=int(num_people)
        )

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = protocolo_pb2_grpc.TravelAgencyStub(channel)
            response = stub.BookTrip(request)

        if response.status == "Success":
            messagebox.showinfo("Sucesso", f"Reserva de viagem realizada com sucesso! Detalhes: {response.details}")
        else:
            messagebox.showerror("Erro", f"Erro na reserva: {response.status}")
    except grpc.RpcError as e:
        messagebox.showerror("Erro", f"Falha na comunicação com o servidor: {e}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

# Configuração da interface gráfica com Tkinter
root = tk.Tk()
root.title("Reserva de Viagem")

# Configuração dos campos
trip_type_var = tk.StringVar(value="round_trip")

tk.Label(root, text="Tipo de Viagem:").grid(row=0, column=0, sticky="w")
trip_type_options = ["round_trip", "one_way"]
trip_type_menu = tk.OptionMenu(root, trip_type_var, *trip_type_options)
trip_type_menu.grid(row=0, column=1)

tk.Label(root, text="Origem:").grid(row=1, column=0, sticky="w")
origin_entry = tk.Entry(root)
origin_entry.grid(row=1, column=1)

tk.Label(root, text="Destino:").grid(row=2, column=0, sticky="w")
destination_entry = tk.Entry(root)
destination_entry.grid(row=2, column=1)

tk.Label(root, text="Data de Partida:").grid(row=3, column=0, sticky="w")
departure_date_entry = tk.Entry(root)
departure_date_entry.grid(row=3, column=1)

tk.Label(root, text="Data de Retorno:").grid(row=4, column=0, sticky="w")
return_date_entry = tk.Entry(root)
return_date_entry.grid(row=4, column=1)

tk.Label(root, text="Número de Pessoas:").grid(row=5, column=0, sticky="w")
num_people_entry = tk.Entry(root)
num_people_entry.grid(row=5, column=1)

# Botão para enviar a solicitação
send_button = tk.Button(root, text="Reservar Viagem", command=send_trip_request)
send_button.grid(row=6, columnspan=2)

# Iniciar a interface gráfica
root.mainloop()
