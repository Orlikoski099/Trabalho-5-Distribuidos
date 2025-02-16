from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc


class AirlineService(protocolo_pb2_grpc.AirlineServicer):
    def __init__(self):
        self.inventory = {
            "São Paulo-Rio de Janeiro": 10
        }

    def BookFlight(self, request, context):
        route = f"{request.origin}-{request.destination}"
        print(
            f"Booking flight. Current inventory for {route}: {self.inventory.get(route, 0)}")
        if route in self.inventory and self.inventory[route] >= request.num_people:
            self.inventory[route] -= request.num_people
            print(
                f"Flight booked. New inventory for {route}: {self.inventory[route]}")
            return protocolo_pb2.FlightResponse(
                status="Success",
                flight_details=f"Flight from {request.origin} to {request.destination} booked."
            )
        else:
            print(
                f"Not enough seats available for {route}. Current inventory: {self.inventory.get(route, 0)}")
            return protocolo_pb2.FlightResponse(
                status="Failure",
                flight_details="Not enough seats available."
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_AirlineServicer_to_server(AirlineService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
