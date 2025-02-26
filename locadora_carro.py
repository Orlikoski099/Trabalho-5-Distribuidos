from concurrent import futures
import grpc
import car_pb2
import car_pb2_grpc
import uuid
import sqlite3


class CarRentalService(car_pb2_grpc.CarRentalServicer):

    def BookCar(self, request, context):
        car_id = str(uuid.uuid4())
        user_id = request.user_id
        print(f'User ID - Locadora: {user_id}')

        car_type = "SUV"  # Permitir diferentes tipos de carro
        pick_up_date = request.pick_up_date
        drop_off_date = request.drop_off_date
        rental_location = "Main Street Car Rental"

        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()

        # Verificar disponibilidade
        cursor.execute('''
            SELECT disponiveis FROM disponibilidade
            WHERE tipo_carro = ? AND data = ?
        ''', (car_type, pick_up_date))

        resultado = cursor.fetchone()
        if resultado is None or int(resultado[0]) <= 0:
            conn.close()
            return car_pb2.CarResponse(
                status="Failure",
                car_id="",
                car_plate="",
                car_details=f"No available cars of type {car_type} on {pick_up_date}."
            )

        # Atualizar disponibilidade (reduzir 1)
        cursor.execute('''
            UPDATE disponibilidade
            SET disponiveis = disponiveis - 1
            WHERE tipo_carro = ? AND data = ?
        ''', (car_type, pick_up_date))

        # Criar reserva
        car_plate = f"ABC-{uuid.uuid4().hex[:6].upper()}"
        cursor.execute('''
            INSERT INTO car_rentals (car_id, user_id, car_type, car_plate, pick_up_date, drop_off_date, rental_location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (car_id, user_id, car_type, car_plate, pick_up_date, drop_off_date, rental_location))

        conn.commit()
        conn.close()

        return car_pb2.CarResponse(
            status="Success",
            car_id=car_id,
            car_plate=car_plate,
            car_details=f"Car type {car_type} with plate {car_plate} from {rental_location} booked from {pick_up_date} to {drop_off_date}."
        )

    def CancelCar(self, request, context):
        car_id = request.car_id
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()

        # Buscar os detalhes da reserva para restaurar a disponibilidade
        cursor.execute('''
            SELECT car_type, pick_up_date FROM car_rentals WHERE car_id = ?
        ''', (car_id,))
        reserva = cursor.fetchone()

        if not reserva:
            conn.close()
            return car_pb2.CancelCarResponse(
                status="Failure",
                message=f"Car rental {car_id} not found."
            )

        car_type, pick_up_date = reserva

        # Remover a reserva
        cursor.execute('''
            DELETE FROM car_rentals WHERE car_id = ?
        ''', (car_id,))

        # Restaurar a disponibilidade
        cursor.execute('''
            UPDATE disponibilidade
            SET disponiveis = disponiveis + 1
            WHERE tipo_carro = ? AND data = ?
        ''', ("Luxo", pick_up_date))

        conn.commit()
        conn.close()

        return car_pb2.CancelCarResponse(
            status="Success",
            message=f"Car rental {car_id} canceled, availability restored."
        )

    def CancelAll(self, request, context):
        user_id = request.user_id
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()

        # Buscar todas as reservas do usuário
        cursor.execute('''
            SELECT car_id, car_type, pick_up_date FROM car_rentals WHERE user_id = ?
        ''', (user_id,))
        reservas = cursor.fetchall()

        if not reservas:
            conn.close()
            return car_pb2.CancelAllResponse(
                status="Failure",
                message=f"No car rentals found for user {user_id}."
            )

        # Restaurar a disponibilidade para cada reserva cancelada
        for car_id, car_type, pick_up_date in reservas:
            cursor.execute('''
                DELETE FROM car_rentals WHERE car_id = ?
            ''', (car_id,))

            cursor.execute('''
                UPDATE disponibilidade
                SET disponiveis = disponiveis + 1
                WHERE tipo_carro = ? AND data = ?
            ''', (car_type, pick_up_date))

        conn.commit()
        conn.close()

        return car_pb2.CancelAllResponse(
            status="Success",
            message=f"All car rentals for user {user_id} have been canceled, availability restored."
        )


def startDB():
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_rentals (
            car_id TEXT PRIMARY KEY,
            user_id TEXT,
            car_type TEXT,
            car_plate TEXT,
            pick_up_date TEXT,
            drop_off_date TEXT,
            rental_location TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disponibilidade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_carro TEXT,
            data TEXT,
            disponiveis INTEGER,
            UNIQUE(tipo_carro, data)
        )
    ''')

    cursor.execute('''
        INSERT INTO disponibilidade (tipo_carro, data, disponiveis)
        VALUES ("Luxo", "27/02/2025", 1)
    ''')

    conn.commit()
    conn.close()


def serve():
    startDB()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    car_pb2_grpc.add_CarRentalServicer_to_server(CarRentalService(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
