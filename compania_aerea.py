from concurrent import futures
import grpc
import airline_pb2
import airline_pb2_grpc

class AirlineService(airline_pb2_grpc.AirlineServicer):
    def BookFlight(self, request, context):
        return airline_pb2.FlightResponse(
            status="Success",
            flight_details=f"Flight from {request.origin} to {request.destination} booked."
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    airline_pb2_grpc.add_AirlineServicer_to_server(AirlineService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
