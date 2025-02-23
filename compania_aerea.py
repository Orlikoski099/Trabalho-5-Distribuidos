from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import uuid

class AirlineService(protocolo_pb2_grpc.AirlineServicer):
    def BookFlight(self, request, context):
        # Gerar um ID único para o voo
        flight_id = str(uuid.uuid4())  # Gerando um ID único com UUID
        
        return protocolo_pb2.FlightResponse(
            status="Success",
            flight_id=flight_id,  # Inclui o flight_id na resposta
            flight_details=f"Flight from {request.origin} to {request.destination} booked."
        )
    
    def CancelFlight(self, request, context):
        # Cancelar o voo com o flight_id fornecido
        return protocolo_pb2.CancelFlightResponse(
            status="Success",
            message=f"Flight {request.flight_id} canceled."
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_AirlineServicer_to_server(AirlineService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
