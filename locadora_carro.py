from concurrent import futures
import grpc
import car_rental_pb2
import car_rental_pb2_grpc


class CarRentalService(car_rental_pb2_grpc.CarRentalServicer):
    def BookCar(self, request, context):
        return car_rental_pb2.CarResponse(
            status="Success",
            car_details=f"Car at {request.destination} booked from {request.pick_up_date} to {request.drop_off_date}."
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    car_rental_pb2_grpc.add_CarRentalServicer_to_server(
        CarRentalService(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
