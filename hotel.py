from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc


class HotelService(protocolo_pb2_grpc.HotelServicer):
    def __init__(self):
        self.inventory = {
            "Rio de Janeiro": 5
        }

    def BookHotel(self, request, context):
        print(
            f"Booking hotel. Current inventory for {request.destination}: {self.inventory.get(request.destination, 0)}")
        if request.destination in self.inventory and self.inventory[request.destination] >= request.num_room:
            self.inventory[request.destination] -= request.num_room
            print(
                f"Hotel booked. New inventory for {request.destination}: {self.inventory[request.destination]}")
            return protocolo_pb2.HotelResponse(
                status="Success",
                hotel_details=f"Hotel at {request.destination} booked from {request.check_in_date} to {request.check_out_date}."
            )
        else:
            print(
                f"Not enough rooms available for {request.destination}. Current inventory: {self.inventory.get(request.destination, 0)}")
            return protocolo_pb2.HotelResponse(
                status="Failure",
                hotel_details="Not enough rooms available."
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_HotelServicer_to_server(HotelService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
