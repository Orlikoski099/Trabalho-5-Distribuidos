from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import uuid
import sqlite3

class HotelService(protocolo_pb2_grpc.HotelServicer):

    def BookHotel(self, request, context):
        # Gerar um ID único para a reserva
        reserva_id = str(uuid.uuid4())  # Gerando um UUID único para a reserva
        user_id = request.user_id  # Recebendo o ID do usuário que está fazendo a reserva
        print(f'User ID - Hotel: {user_id}')

        # Gerar internamente o nome do hotel e número do quarto
        hotel_name = "Hotel XYZ"  # Nome do hotel gerado pelo serviço
        room_number = f"Room-{uuid.uuid4().hex[:6]}"  # Número do quarto gerado aleatoriamente
        check_in_date = request.check_in_date  # Data de check-in
        check_out_date = request.check_out_date  # Data de check-out

        # Inserir os dados no banco de dados
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reservas (reserva_id, user_id, hotel_name, room_number, check_in_date, check_out_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (reserva_id, user_id, hotel_name, room_number, check_in_date, check_out_date))

        conn.commit()
        conn.close()

        return protocolo_pb2.HotelResponse(
            status="Success",
            hotel_id=reserva_id,  # Inclui o reserva_id (UUID) na resposta
            hotel_name=hotel_name, 
            hotel_details=f"Hotel {hotel_name} with room number {room_number} booked from {check_in_date} to {check_out_date}."
        )
    
    def CancelHotel(self, request, context):
        # Cancelar a reserva com o reserva_id fornecido
        reserva_id = request.hotel_id  # ID da reserva
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM reservas WHERE reserva_id = ?
        ''', (reserva_id,))

        conn.commit()
        conn.close()

        return protocolo_pb2.CancelHotelResponse(
            status="Success",
            message=f"Hotel reservation {reserva_id} canceled."
        )

    def CancelAll(self, user_id, context):
        # Aqui fazemos o DELETE de todos os voos associados ao user_id
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM hotels WHERE user_id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()

        return True  # Retorna True se o cancelamento foi bem-sucedido

# Função para criar o banco de dados
def startDB():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            reserva_id TEXT PRIMARY KEY,  -- Usando UUID como chave primária
            user_id TEXT,  -- ID do usuário que fez a reserva
            hotel_name TEXT,  -- Nome do hotel
            room_number TEXT,  -- Número do quarto
            check_in_date TEXT,  -- Data de check-in
            check_out_date TEXT  -- Data de check-out
        )
    ''')

    conn.commit()
    conn.close()

def serve():
    startDB()  # Cria o banco de dados e a tabela ao iniciar o servidor
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_HotelServicer_to_server(HotelService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
