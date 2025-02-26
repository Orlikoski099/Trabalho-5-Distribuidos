from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import uuid
import sqlite3


class HotelService(protocolo_pb2_grpc.HotelServicer):

    def BookHotel(self, request, context):
        reserva_id = str(uuid.uuid4())
        user_id = request.user_id
        print(f'User ID - Hotel: {user_id}')


        hotel_name = "Hotel XYZ"
        room_number = f"Room-{uuid.uuid4().hex[:6]}"
        check_in_date = request.check_in_date
        check_out_date = request.check_out_date

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
            hotel_id=reserva_id,
            hotel_name=hotel_name,
            hotel_details=f"Hotel {hotel_name} with room number {room_number} booked from {check_in_date} to {check_out_date}."
        )

    # Cancelar a reserva com o reserva_id fornecido (SAGA)
    def CancelHotel(self, request, context):
        reserva_id = request.hotel_id
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

    def CancelAll(self, request, context):
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM reservas WHERE user_id = ?
        ''', (request.user_id,))

        conn.commit()
        conn.close()

        return protocolo_pb2.CancelAllResponse(
            status="Success",
            message=f"All Hotel reservations for user {request.user_id} have been canceled."
        )

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
    startDB()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_HotelServicer_to_server(HotelService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
