from concurrent import futures
import grpc
import flight_pb2
import flight_pb2_grpc
import uuid
import sqlite3


class AirlineService(flight_pb2_grpc.AirlineServicer):

    def BookFlight(self, request, context):
        flight_id = str(uuid.uuid4())
        user_id = request.user_id
        print(f'User ID - Airline: {user_id}')

        airline_name = "Airline XYZ"
        flight_number = f"FL-{uuid.uuid4().hex[:6]}"
        departure_date = request.departure_date
        origin = request.origin
        destination = request.destination
        class_type = "Luxo"

        conn = sqlite3.connect('flight.db')
        cursor = conn.cursor()

        # Verificar disponibilidade
        cursor.execute('''
            SELECT disponiveis FROM disponibilidade
            WHERE tipo_classe = ? AND data = ?
        ''', (class_type, departure_date))

        resultado = cursor.fetchone()

        if resultado is None:
            conn.close()
            return flight_pb2.FlightResponse(
                status="Failure",
                flight_id="",
                flight_number="",
                flight_details=f"No availability information for class {class_type} on {departure_date}."
            )

        disponiveis = int(resultado[0])

        if disponiveis <= 0:
            conn.close()
            return flight_pb2.FlightResponse(
                status="Failure",
                flight_id="",
                flight_number="",
                flight_details=f"No available seats in class {class_type} on {departure_date}."
            )

        # Atualizar disponibilidade (reduzir 1)
        cursor.execute('''
            UPDATE disponibilidade
            SET disponiveis = disponiveis - 1
            WHERE tipo_classe = ? AND data = ?
        ''', (class_type, departure_date))

        # Criar reserva
        cursor.execute('''
            INSERT INTO flights (flight_id, user_id, airline_name, flight_number, departure_date, origin, destination)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (flight_id, user_id, airline_name, flight_number, departure_date, origin, destination))

        conn.commit()
        conn.close()

        return flight_pb2.FlightResponse(
            status="Success",
            flight_id=flight_id,
            flight_number=flight_number,
            flight_details=f"Flight {flight_number} with {airline_name} from {origin} to {destination} booked for {departure_date}."
        )

    def CancelFlight(self, request, context):
        flight_id = request.flight_id
        conn = sqlite3.connect('flight.db')
        cursor = conn.cursor()

        # Buscar detalhes da reserva para restaurar a disponibilidade
        cursor.execute('''
            SELECT tipo_classe, departure_date FROM flights WHERE flight_id = ?
        ''', (flight_id,))
        reserva = cursor.fetchone()

        if not reserva:
            conn.close()
            return flight_pb2.CancelFlightResponse(
                status="Failure",
                message=f"Flight reservation {flight_id} not found."
            )

        tipo_classe, departure_date = reserva

        # Remover a reserva
        cursor.execute('''
            DELETE FROM flights WHERE flight_id = ?
        ''', (flight_id,))

        # Restaurar a disponibilidade
        cursor.execute('''
            UPDATE disponibilidade
            SET disponiveis = disponiveis + 1
            WHERE tipo_classe = ? AND data = ?
        ''', ("Luxo", departure_date))

        conn.commit()
        conn.close()

        return flight_pb2.CancelFlightResponse(
            status="Success",
            message=f"Flight reservation {flight_id} canceled, availability restored."
        )

    def CancelAll(self, request, context):
        user_id = request.user_id
        conn = sqlite3.connect('flight.db')
        cursor = conn.cursor()

        # Buscar todas as reservas do usuário
        cursor.execute('''
            SELECT flight_id, tipo_classe, departure_date FROM flights WHERE user_id = ?
        ''', (user_id,))
        reservas = cursor.fetchall()

        if not reservas:
            conn.close()
            return flight_pb2.CancelAllResponse(
                status="Failure",
                message=f"No reservations found for user {user_id}."
            )

        # Restaurar a disponibilidade para cada reserva cancelada
        for flight_id, tipo_classe, departure_date in reservas:
            cursor.execute('''
                DELETE FROM flights WHERE flight_id = ?
            ''', (flight_id,))

            cursor.execute('''
                UPDATE disponibilidade
                SET disponiveis = disponiveis + 1
                WHERE tipo_classe = ? AND data = ?
            ''', (tipo_classe, departure_date))

        conn.commit()
        conn.close()

        return flight_pb2.CancelAllResponse(
            status="Success",
            message=f"All flight reservations for user {user_id} have been canceled, availability restored."
        )


def startDB():
    conn = sqlite3.connect('flight.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            flight_id TEXT PRIMARY KEY,
            user_id TEXT,
            airline_name TEXT,
            flight_number TEXT,
            departure_date TEXT,
            origin TEXT,
            destination TEXT,
            tipo_classe TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disponibilidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_classe TEXT,
            data TEXT,
            disponiveis INTEGER
        )
    ''')

    # Inserção de exemplo para testar disponibilidade
    cursor.execute('''
        INSERT OR IGNORE INTO disponibilidade (tipo_classe, data, disponiveis)
        VALUES ("Luxo", "27/02/2025", 2)
    ''')

    conn.commit()
    conn.close()


def serve():
    startDB()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    flight_pb2_grpc.add_AirlineServicer_to_server(AirlineService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
