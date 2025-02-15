from concurrent import futures
import grpc
import hotel_pb2
import hotel_pb2_grpc


class HotelService(hotel_pb2_grpc.HotelServicer):
    def BookHotel(self, request, context):
        return hotel_pb2.HotelResponse(
            status="Success",
            hotel_details=f"Hotel at {request.destination} booked from {request.check_in_date} to {request.check_out_date}."
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hotel_pb2_grpc.add_HotelServicer_to_server(HotelService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
