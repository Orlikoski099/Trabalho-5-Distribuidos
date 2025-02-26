from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import uuid
import sqlite3


class CarRentalService(protocolo_pb2_grpc.CarRentalServicer):

    def BookCar(self, request, context):
        car_id = str(uuid.uuid4())
        user_id = request.user_id
        print(f'User ID - Locadora: {user_id}')

        car_type = "Sedan"
        car_plate = f"ABC-{uuid.uuid4().hex[:6].upper()}"
        pick_up_date = request.pick_up_date
        drop_off_date = request.drop_off_date
        rental_location = "Main Street Car Rental"

        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO car_rentals (car_id, user_id, car_type, car_plate, pick_up_date, drop_off_date, rental_location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (car_id, user_id, car_type, car_plate, pick_up_date, drop_off_date, rental_location))

        conn.commit()
        conn.close()

        return protocolo_pb2.CarResponse(
            status="Success",
            car_id=car_id,
            car_plate=car_plate,
            car_details=f"Car type {car_type} with plate {car_plate} from {rental_location} booked from {pick_up_date} to {drop_off_date}."
        )

    def CancelCar(self, request, context):
        car_id = request.car_id
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM car_rentals WHERE car_id = ?
        ''', (car_id,))

        conn.commit()
        conn.close()

        return protocolo_pb2.CancelCarResponse(
            status="Success",
            message=f"Car rental {car_id} canceled."
        )

    def CancelAll(self, request, context):
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM car_rentals WHERE user_id = ?
        ''', (request.user_id,))

        conn.commit()
        conn.close()

        return protocolo_pb2.CancelAllResponse(
            status="Success",
            message=f"All cars for user {request.user_id} have been canceled."
        )


def startDB():
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_rentals (
            car_id TEXT PRIMARY KEY,  -- Usando UUID como chave primária
            user_id TEXT,  -- ID do usuário que fez a reserva
            car_type TEXT,  -- Tipo do carro
            car_plate TEXT,  -- Placa do carro
            pick_up_date TEXT,  -- Data de retirada
            drop_off_date TEXT,  -- Data de devolução
            rental_location TEXT  -- Local da locadora
        )
    ''')

    conn.commit()
    conn.close()


def serve():
    startDB()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_CarRentalServicer_to_server(
        CarRentalService(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
