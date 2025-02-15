# travel_agency.py
from concurrent import futures
import grpc
import trip_pb2
import trip_pb2_grpc
import airline_pb2
import airline_pb2_grpc
import hotel_pb2
import hotel_pb2_grpc
import car_rental_pb2
import car_rental_pb2_grpc


class TravelAgencyService(trip_pb2_grpc.TravelAgencyServicer):
    def BookTrip(self, request, context):
        # Interage com a companhia aérea
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = airline_pb2_grpc.AirlineStub(channel)
            flight_response = stub.BookFlight(
                airline_pb2.FlightRequest(
                    trip_type=request.trip_type,
                    origin=request.origin,
                    destination=request.destination,
                    departure_date=request.departure_date,
                    return_date=request.return_date,
                    num_people=request.num_people
                )
            )

        # Interage com a rede hoteleira
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = hotel_pb2_grpc.HotelStub(channel)
            hotel_response = stub.BookHotel(
                hotel_pb2.HotelRequest(
                    destination=request.destination,
                    check_in_date=request.departure_date,
                    check_out_date=request.return_date,
                    num_people=request.num_people
                )
            )

        # Interage com a locadora de carro
        with grpc.insecure_channel('localhost:50054') as channel:
            stub = car_rental_pb2_grpc.CarRentalStub(channel)
            car_response = stub.BookCar(
                car_rental_pb2.CarRequest(
                    destination=request.destination,
                    pick_up_date=request.departure_date,
                    drop_off_date=request.return_date,
                    num_people=request.num_people
                )
            )

        return trip_pb2.TripResponse(
            status="Success",
            details=f"Flight: {flight_response.flight_details}, Hotel: {hotel_response.hotel_details}, Car: {car_response.car_details}"
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    trip_pb2_grpc.add_TravelAgencyServicer_to_server(
        TravelAgencyService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
