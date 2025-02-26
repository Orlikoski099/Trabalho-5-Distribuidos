from concurrent import futures
import grpc
import hotel_pb2
import hotel_pb2_grpc
import uuid
import sqlite3


class HotelService(hotel_pb2_grpc.HotelServicer):

    def BookHotel(self, request, context):
        reserva_id = str(uuid.uuid4())
        user_id = request.user_id
        print(f'User ID - Hotel: {user_id}')
        hotel_name = "Hotel XYZ"
        tipo_quarto = "Luxo"
        room_number = "Luxo"
        check_in_date = request.check_in_date
        check_out_date = request.check_out_date

        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()

        # Verificar disponibilidade
        cursor.execute('''
            SELECT disponiveis FROM disponibilidade
            WHERE tipo_quarto = ? AND data = ?
        ''', ("Luxo", check_in_date))

        resultado = cursor.fetchone()

        if resultado is None:
            conn.close()
            return hotel_pb2.HotelResponse(
                status="Failure",
                hotel_id="",
                hotel_name="",
                hotel_details=f"No availability information for room type {tipo_quarto} on {check_in_date}."
            )

        disponiveis = int(resultado[0])

        if disponiveis <= 0:
            conn.close()
            return hotel_pb2.HotelResponse(
                status="Failure",
                hotel_id="",
                hotel_name="",
                hotel_details=f"No available rooms of type {tipo_quarto} on {check_in_date}."
            )

        # Atualizar disponibilidade (reduzir 1)
        cursor.execute('''
            UPDATE disponibilidade
            SET disponiveis = disponiveis - 1
            WHERE tipo_quarto = ? AND data = ?
        ''', (tipo_quarto, check_in_date))

        # Criar reserva
        hotel_name = "Hotel XYZ"
        room_number = f"Room-{uuid.uuid4().hex[:6]}"

        cursor.execute('''
            INSERT INTO reservas (reserva_id, user_id, hotel_name, room_number, check_in_date, check_out_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (reserva_id, user_id, hotel_name, room_number, check_in_date, request.check_out_date))

        conn.commit()
        conn.close()

        return hotel_pb2.HotelResponse(
            status="Success",
            hotel_id=reserva_id,
            hotel_name=hotel_name,
            hotel_details=f"Hotel {hotel_name} with room number {room_number} booked from {check_in_date} to {request.check_out_date}."
        )

    def CancelHotel(self, request, context):
        reserva_id = request.hotel_id
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()

        # Buscar os detalhes da reserva para restaurar a disponibilidade
        cursor.execute('''
            SELECT tipo_quarto, check_in_date FROM reservas WHERE reserva_id = ?
        ''', (reserva_id,))
        reserva = cursor.fetchone()

        if not reserva:
            conn.close()
            return hotel_pb2.CancelHotelResponse(
                status="Failure",
                message=f"Reservation {reserva_id} not found."
            )

        tipo_quarto, check_in_date = reserva

        # Remover a reserva
        cursor.execute('''
            DELETE FROM reservas WHERE reserva_id = ?
        ''', (reserva_id,))

        # Restaurar a disponibilidade
        cursor.execute('''
            UPDATE disponibilidade
            SET disponiveis = disponiveis + 1
            WHERE tipo_quarto = ? AND data = ?
        ''', (tipo_quarto, check_in_date))

        conn.commit()
        conn.close()

        return hotel_pb2.CancelHotelResponse(
            status="Success",
            message=f"Hotel reservation {reserva_id} canceled, availability restored."
        )

    def CancelAll(self, request, context):
        user_id = request.user_id
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()

        # Buscar todas as reservas do usuário
        cursor.execute('''
            SELECT reserva_id, tipo_quarto, check_in_date FROM reservas WHERE user_id = ?
        ''', (user_id,))
        reservas = cursor.fetchall()

        if not reservas:
            conn.close()
            return hotel_pb2.CancelAllResponse(
                status="Failure",
                message=f"No reservations found for user {user_id}."
            )

        # Restaurar a disponibilidade para cada reserva cancelada
        for reserva_id, tipo_quarto, check_in_date in reservas:
            cursor.execute('''
                DELETE FROM reservas WHERE reserva_id = ?
            ''', (reserva_id,))

            cursor.execute('''
                UPDATE disponibilidade
                SET disponiveis = disponiveis + 1
                WHERE tipo_quarto = ? AND data = ?
            ''', (tipo_quarto, check_in_date))

        conn.commit()
        conn.close()

        return hotel_pb2.CancelAllResponse(
            status="Success",
            message=f"All hotel reservations for user {user_id} have been canceled, availability restored."
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
            check_out_date TEXT,  -- Data de check-out
            tipo_quarto TEXT  -- Tipo de quarto
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disponibilidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_quarto TEXT,
            data TEXT,
            disponiveis INTEGER
        )
    ''')

    # Inserção de exemplo para testar disponibilidade
    cursor.execute('''
        INSERT OR IGNORE INTO disponibilidade (tipo_quarto, data, disponiveis)
        VALUES ("Luxo", "27/02/2025", 2)
    ''')

    conn.commit()
    conn.close()


def serve():
    startDB()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hotel_pb2_grpc.add_HotelServicer_to_server(HotelService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
