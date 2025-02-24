from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import uuid
import sqlite3

class AirlineService(protocolo_pb2_grpc.AirlineServicer):

    def BookFlight(self, request, context):
        # Gerar um ID único para a reserva de voo
        flight_id = str(uuid.uuid4())  # Gerando um UUID único para a reserva de voo
        user_id = request.user_id  # Recebendo o ID do usuário que está fazendo a reserva
        print(f'User ID - Airline: {user_id}')

        # Gerar internamente os parâmetros do voo
        airline_name = "Airline XYZ"  # Nome da companhia aérea gerado pelo serviço
        flight_number = f"FL-{uuid.uuid4().hex[:6]}"  # Número do voo gerado aleatoriamente
        departure_date = request.departure_date  # Data de embarque
        origin = request.origin 
        destination = request.destination 

        # Inserir os dados no banco de dados
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
            flight_id=flight_id,  # Inclui o flight_id (UUID) na resposta
            flight_number=flight_number,  # Inclui o flight_id (UUID) na resposta
            flight_details=f"Flight {flight_number} with {airline_name} from {origin} to {destination} booked for {departure_date}."
        )
    
    def CancelFlight(self, request, context):
        # Cancelar a reserva do voo com o flight_id fornecido
        flight_id = request.flight_id  # ID da reserva do voo
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

    def CancelAll(self, user_id, context):
        # Aqui fazemos o DELETE de todos os voos associados ao user_id
        conn = sqlite3.connect('flight.db')
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM flights WHERE user_id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()

        return True  # Retorna True se o cancelamento foi bem-sucedido

    

# Função para criar o banco de dados
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
    startDB()  # Cria o banco de dados e a tabela ao iniciar o servidor
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_AirlineServicer_to_server(AirlineService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
