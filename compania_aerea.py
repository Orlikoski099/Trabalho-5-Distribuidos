from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import uuid
import sqlite3


class AirlineService(protocolo_pb2_grpc.AirlineServicer):

    def BookFlight(self, request, context):
        flight_id = str(uuid.uuid4())
        user_id = request.user_id
        print(f'User ID - Airline: {user_id}')

        airline_name = "Airline XYZ"
        flight_number = f"FL-{uuid.uuid4().hex[:6]}"
        departure_date = request.departure_date
        origin = request.origin
        destination = request.destination

        conn = sqlite3.connect('flight.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO flights (flight_id, user_id, airline_name, flight_number, departure_date, origin, destination)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (flight_id, user_id, airline_name, flight_number, departure_date, origin, destination))

        conn.commit()
        conn.close()

        return protocolo_pb2.FlightResponse(
            status="Success",
            flight_id=flight_id,
            flight_number=flight_number,
            flight_details=f"Flight {flight_number} with {airline_name} from {origin} to {destination} booked for {departure_date}."
        )

    def CancelFlight(self, request, context):
        flight_id = request.flight_id
        conn = sqlite3.connect('flight.db')
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM flights WHERE flight_id = ?
        ''', (flight_id,))

        conn.commit()
        conn.close()

        return protocolo_pb2.CancelFlightResponse(
            status="Success",
            message=f"Flight reservation {flight_id} canceled."
        )

    def CancelAll(self, request, context):
        conn = sqlite3.connect('flight.db')
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM flights WHERE user_id = ?
        ''', (request.user_id,))

        conn.commit()
        conn.close()

        return protocolo_pb2.CancelAllResponse(
            status="Success",
            message=f"All flights for user {request.user_id} have been canceled."
        )


def startDB():
    conn = sqlite3.connect('flight.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            flight_id TEXT PRIMARY KEY,  -- Usando UUID como chave primária
            user_id TEXT,  -- ID do usuário que fez a reserva
            airline_name TEXT,  -- Nome da companhia aérea
            flight_number TEXT,  -- Número do voo
            departure_date TEXT,  -- Data de embarque
            origin TEXT,  -- Origem do voo
            destination TEXT  -- Destino do voo
        )
    ''')

    conn.commit()
    conn.close()


def serve():
    startDB()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_AirlineServicer_to_server(AirlineService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
