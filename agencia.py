from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
from grpc import RpcError

class TravelAgencyServicer(protocolo_pb2_grpc.TravelAgencyServicer):

    def CancelBookTrip(self, request, context):
        user_id = request.user_id  # Recupera o user_id da requisição

        # Chama as funções para cancelar as viagens
        flight_response = self.cancel_all_flights(user_id)
        hotel_response = self.cancel_all_hotels(user_id)
        car_response = self.cancel_all_cars(user_id)

        # Retorna uma resposta consolidada com o status de cada cancelamento
        status = "Success"
        if not flight_response or not hotel_response or not car_response:
            status = "Partial Success"

        return protocolo_pb2.CancelTripResponse(
            status=status,
            message=f"All trips for user {user_id} have been canceled."
        )

    def BookTrip(self, request, context):
        if not request.user_id or not request.trip_type or not request.origin or not request.destination or not request.departure_date or not request.num_people:
            print("Erro: Dados ausentes na solicitação de viagem.")
            return protocolo_pb2.TripResponse(status="Failure", details="Dados ausentes na solicitação de viagem.")
        elif request.trip_type != "one_way" and not request.return_date:
            print("Erro: Data de retorno ausente na solicitação de viagem.")
            return protocolo_pb2.TripResponse(status="Failure", details="Data de retorno ausente para viagem de ida e volta.")

        print("Dados da viagem validados com sucesso.")

        flight_id = None
        hotel_id = None
        car_id = None
        flight_number = None
        hotel_name = None
        car_plate = None

        try:
            # Etapa 1: Reserva do voo
            try:
                print(request.user_id)
                flight_response = self.book_flight(request)
                print('FLIGHT STATUS: ', flight_response.status)
                flight_id = flight_response.flight_id  # Salva o ID do voo
                flight_number = flight_response.flight_number  # Salva o nome da cia aérea
                if flight_response.status != "Success":
                    print("Failed to book flight")
                    raise Exception("Failed to book flight")
            except (RpcError, Exception) as e:
                print(f"Flight booking failed: {e}")
                raise Exception("Failed to book flight")

            # Etapa 2: Reserva do hotel
            try:
                hotel_response = self.book_hotel(request)
                print('HOTEL STATUS: ', hotel_response.status)
                hotel_id = hotel_response.hotel_id  # Salva o ID do hotel
                hotel_name = hotel_response.hotel_name  # Salva o nome do hotel
                if hotel_response.status != "Success":
                    print("Failed to book hotel")
                    raise Exception("Failed to book hotel")
            except (RpcError, Exception) as e:  # Captura erro de comunicação ou falha no hotel
                if flight_id:  # Cancela o voo apenas se foi reservado com sucesso
                    self.cancel_flight(flight_id)
                print(f"Hotel booking failed: {e}")
                raise Exception("Hotel booking failed")

            # Etapa 3: Reserva do carro
            try:
                car_response = self.book_car(request)
                print('CAR STATUS: ', car_response.status)
                car_id = car_response.car_id  # Salva o ID do carro
                car_plate = car_response.car_plate  # Salva o nome do carro
                if car_response.status != "Success":
                    print("Failed to book car")
                    raise Exception("Failed to book car")
            except (RpcError, Exception) as e:  # Captura erro de comunicação ou falha no carro
                if hotel_id:  # Cancela o hotel apenas se foi reservado com sucesso
                    self.cancel_hotel(hotel_id)
                if flight_id:  # Cancela o voo apenas se foi reservado com sucesso
                    self.cancel_flight(flight_id)
                print(f"Car booking failed: {e}")
                raise Exception("Car booking failed")

        except Exception as e:
            return protocolo_pb2.TripResponse(status=f"Failure - {e}", details="Trip NOT booked")

        # Retornar os dados completos, incluindo user_id e detalhes das reservas
        return protocolo_pb2.TripResponse(
            status="Success", 
            details="Trip booked successfully",
            flight_id=flight_id,
            flight_number=flight_number,
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            car_id=car_id,
            car_plate=car_plate
        )

    def cancel_all_flights(self, user_id):
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = protocolo_pb2_grpc.AirlineStub(channel)
            cancel_request = protocolo_pb2.CancelAllRequest(user_id=user_id)
            cancel_response = stub.CancelAll(cancel_request)
            return cancel_response

    def cancel_all_hotels(self, user_id):
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = protocolo_pb2_grpc.HotelStub(channel)
            cancel_request = protocolo_pb2.CancelAllRequest(user_id=user_id)
            cancel_response = stub.CancelAll(cancel_request)
            return cancel_response

    def cancel_all_cars(self, user_id):
        with grpc.insecure_channel('localhost:50054') as channel:
            stub = protocolo_pb2_grpc.CarRentalStub(channel)
            cancel_request = protocolo_pb2.CancelAllRequest(user_id=user_id)
            cancel_response = stub.CancelAll(cancel_request)
            return cancel_response

    def cancel_flight(self, flight_id):
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = protocolo_pb2_grpc.AirlineStub(channel)
            cancel_request = protocolo_pb2.CancelFlightRequest(flight_id=flight_id)
            cancel_response = stub.CancelFlight(cancel_request)
            return cancel_response

    def cancel_hotel(self, hotel_id):
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = protocolo_pb2_grpc.HotelStub(channel)
            cancel_request = protocolo_pb2.CancelHotelRequest(hotel_id=hotel_id)
            cancel_response = stub.CancelHotel(cancel_request)
            return cancel_response

    def cancel_car(self, car_id):
        with grpc.insecure_channel('localhost:50054') as channel:
            stub = protocolo_pb2_grpc.CarRentalStub(channel)
            cancel_request = protocolo_pb2.CancelCarRequest(car_id=car_id)
            cancel_response = stub.CancelCar(cancel_request)
            return cancel_response

    def book_flight(self, request):
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = protocolo_pb2_grpc.AirlineStub(channel)
            flight_request = protocolo_pb2.FlightRequest(
                user_id=request.user_id,  # Adicionando user_id
                trip_type=request.trip_type,
                origin=request.origin, 
                destination=request.destination,
                departure_date=request.departure_date, 
                return_date=request.return_date,
                num_people=request.num_people
            )
            flight_response = stub.BookFlight(flight_request)
            return flight_response

    def book_hotel(self, request):
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = protocolo_pb2_grpc.HotelStub(channel)
            hotel_request = protocolo_pb2.HotelRequest(
                user_id=request.user_id,  # Adicionando user_id
                destination=request.destination, 
                check_in_date=request.departure_date,
                check_out_date=request.return_date, 
                num_people=request.num_people
            )
            hotel_response = stub.BookHotel(hotel_request)
            return hotel_response

    def book_car(self, request):
        with grpc.insecure_channel('localhost:50054') as channel:
            stub = protocolo_pb2_grpc.CarRentalStub(channel)
            car_request = protocolo_pb2.CarRequest(
                user_id=request.user_id,  # Adicionando user_id
                destination=request.destination, 
                pick_up_date=request.departure_date,
                drop_off_date=request.return_date, 
                num_people=request.num_people
            )
            car_response = stub.BookCar(car_request)
            return car_response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_TravelAgencyServicer_to_server(TravelAgencyServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
