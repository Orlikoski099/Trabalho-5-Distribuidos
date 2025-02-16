from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc


class TravelAgencyService(protocolo_pb2_grpc.TravelAgencyServicer):
    def BookTrip(self, request, context):
        flight_response = self.book_flight(request)
        if flight_response.status != "Success":
            return protocolo_pb2.TripResponse(status="Failure", details=flight_response.flight_details)

        hotel_response = self.book_hotel(request)
        if hotel_response.status != "Success":
            return protocolo_pb2.TripResponse(status="Failure", details=hotel_response.hotel_details)

        car_response = self.book_car(request)
        if car_response.status != "Success":
            return protocolo_pb2.TripResponse(status="Failure", details=car_response.car_details)

        return protocolo_pb2.TripResponse(
            status="Success",
            details=f"Flight: {flight_response.flight_details}, Hotel: {hotel_response.hotel_details}, Car: {car_response.car_details}"
        )

    def book_flight(self, request):
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = protocolo_pb2_grpc.AirlineStub(channel)
            return stub.BookFlight(
                protocolo_pb2.FlightRequest(
                    trip_type=request.trip_type,
                    origin=request.origin,
                    destination=request.destination,
                    departure_date=request.departure_date,
                    return_date=request.return_date,
                    num_people=request.num_people,
                    num_car=request.num_car
                )
            )

    def book_hotel(self, request):
        with grpc.insecure_channel('localhost:50053') as channel:
            stub = protocolo_pb2_grpc.HotelStub(channel)
            return stub.BookHotel(
                protocolo_pb2.HotelRequest(
                    destination=request.destination,
                    check_in_date=request.departure_date,
                    check_out_date=request.return_date,
                    num_people=request.num_people,
                    num_room=request.num_room
                )
            )

    def book_car(self, request):
        with grpc.insecure_channel('localhost:50054') as channel:
            stub = protocolo_pb2_grpc.CarRentalStub(channel)
            return stub.BookCar(
                protocolo_pb2.CarRequest(
                    destination=request.destination,
                    pick_up_date=request.departure_date,
                    drop_off_date=request.return_date,
                    num_car=request.num_car
                )
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_TravelAgencyServicer_to_server(
        TravelAgencyService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
