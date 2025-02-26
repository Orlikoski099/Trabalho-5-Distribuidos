import grpc
import travel_pb2
import travel_pb2_grpc
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Sistema de Viagens")
root.geometry("400x600")
root.configure(bg="#f0f0f0")


def open_cancel_window():
    cancel_window = tk.Toplevel(root)
    cancel_window.title("Cancelar Reserva")
    cancel_window.geometry("300x200")
    cancel_window.configure(bg="#f0f0f0")

    tk.Label(cancel_window, text="ID do Usuário:",
             font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
    user_id_entry = tk.Entry(cancel_window, font=("Arial", 12))
    user_id_entry.pack(pady=5)

    def send_cancellation_request():
        user_id = user_id_entry.get()
        if not user_id:
            messagebox.showerror(
                "Erro", "O campo de ID de usuário deve ser preenchido!")
            return

        try:
            request = travel_pb2.CancelTripRequest(user_id=user_id)
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = travel_pb2_grpc.TravelAgencyStub(channel)
                response = stub.CancelBookTrip(request)

            if response.status == "Success":
                messagebox.showinfo("Sucesso", "Reserva excluída com sucesso!")
            else:
                messagebox.showerror(
                    "Erro", f"Erro ao excluir reserva: {response.status}")
        except grpc.RpcError as e:
            messagebox.showerror(
                "Erro", f"Falha na comunicação com o servidor: {e}")

    tk.Button(cancel_window, text="Cancelar Reserva", font=("Arial", 12),
              bg="#ff4d4d", fg="white", command=send_cancellation_request).pack(pady=5)
    tk.Button(cancel_window, text="Voltar", font=("Arial", 12),
              bg="#4CAF50", fg="white", command=cancel_window.destroy).pack(pady=5)


trip_type_var = tk.StringVar(value="round_trip")

tk.Label(root, text="Tipo de Viagem:", font=(
    "Arial", 12), bg="#f0f0f0").pack(pady=5)
tk.OptionMenu(root, trip_type_var, "round_trip", "one_way").pack(pady=5)
tk.Label(root, text="Origem:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
origin_entry = tk.Entry(root, font=("Arial", 12))
origin_entry.pack(pady=5)
tk.Label(root, text="Destino:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
destination_entry = tk.Entry(root, font=("Arial", 12))
destination_entry.pack(pady=5)
tk.Label(root, text="Data de Partida:", font=(
    "Arial", 12), bg="#f0f0f0").pack(pady=5)
departure_date_entry = tk.Entry(root, font=("Arial", 12))
departure_date_entry.pack(pady=5)
tk.Label(root, text="Data de Retorno:", font=(
    "Arial", 12), bg="#f0f0f0").pack(pady=5)
return_date_entry = tk.Entry(root, font=("Arial", 12))
return_date_entry.pack(pady=5)
tk.Label(root, text="Número de Pessoas:", font=(
    "Arial", 12), bg="#f0f0f0").pack(pady=5)
num_people_entry = tk.Entry(root, font=("Arial", 12))
num_people_entry.pack(pady=5)
tk.Label(root, text="ID do Usuário:", font=(
    "Arial", 12), bg="#f0f0f0").pack(pady=5)
user_id_entry = tk.Entry(root, font=("Arial", 12))
user_id_entry.pack(pady=5)


def send_trip_request():
    trip_type = trip_type_var.get()
    origin = origin_entry.get()
    destination = destination_entry.get()
    departure_date = departure_date_entry.get()
    return_date = return_date_entry.get()
    num_people = num_people_entry.get()
    user_id = user_id_entry.get()

    if not origin or not destination or not departure_date or not num_people or not user_id:
        messagebox.showerror(
            "Erro", "Todos os campos obrigatórios devem ser preenchidos!")
        return

    try:
        request = travel_pb2.TripRequest(
            trip_type=trip_type,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date if return_date else "",
            num_people=int(num_people),
            user_id=user_id,
        )

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = travel_pb2_grpc.TravelAgencyStub(channel)
            response = stub.BookTrip(request)

        if response.status == "Success":
            messagebox.showinfo(
                "Sucesso", f"Reserva realizada com sucesso!\n\nDetalhes: {response.details}")
        else:
            messagebox.showerror(
                "Erro", f"Erro na reserva: {response.details}")
    except grpc.RpcError as e:
        messagebox.showerror(
            "Erro", f"Falha na comunicação com o servidor: {e}")


tk.Button(root, text="Reservar Viagem", font=("Arial", 12),
          bg="#4CAF50", fg="white", command=send_trip_request).pack(pady=10)
tk.Button(root, text="Cancelar Reserva", font=("Arial", 12),
          bg="#ff4d4d", fg="white", command=open_cancel_window).pack(pady=10)

root.mainloop()
