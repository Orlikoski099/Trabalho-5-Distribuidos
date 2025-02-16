from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc


class CarRentalService(protocolo_pb2_grpc.CarRentalServicer):
    def __init__(self):
        self.inventory = {
            "Rio de Janeiro": 7
        }

    def BookCar(self, request, context):
        print(
            f"Booking car. Current inventory for {request.destination}: {self.inventory.get(request.destination, 0)}")
        if request.destination in self.inventory and self.inventory[request.destination] >= request.num_car:
            self.inventory[request.destination] -= request.num_car
            print(
                f"Car booked. New inventory for {request.destination}: {self.inventory[request.destination]}")
            return protocolo_pb2.CarResponse(
                status="Success",
                car_details=f"Car at {request.destination} booked from {request.pick_up_date} to {request.drop_off_date}."
            )
        else:
            print(
                f"Not enough cars available for {request.destination}. Current inventory: {self.inventory.get(request.destination, 0)}")
            return protocolo_pb2.CarResponse(
                status="Failure",
                car_details="Not enough cars available."
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_CarRentalServicer_to_server(
        CarRentalService(), server)
    server.add_insecure_port('[::]:50054')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
