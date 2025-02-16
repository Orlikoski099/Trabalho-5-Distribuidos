import grpc
import protocolo_pb2
import protocolo_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = protocolo_pb2_grpc.TravelAgencyStub(channel)
        response = stub.BookTrip(
            protocolo_pb2.TripRequest(
                trip_type="round_trip",
                origin="São Paulo",
                destination="Rio de Janeiro",
                departure_date="2023-12-25",
                return_date="2023-12-31",
                num_people=2,
                num_car=1,
                num_room=1
            )
        )
    print("Trip Booking Response: ", response)


if __name__ == '__main__':
    run()
