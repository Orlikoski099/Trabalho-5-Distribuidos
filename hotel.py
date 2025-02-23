from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import uuid

class HotelService(protocolo_pb2_grpc.HotelServicer):
    def BookHotel(self, request, context):
        # Gerar um ID único para o hotel
        hotel_id = str(uuid.uuid4())  # Gerando um ID único com UUID
        
        return protocolo_pb2.HotelResponse(
            status="Success",
            hotel_id=hotel_id,  # Inclui o hotel_id na resposta
            hotel_details=f"Hotel at {request.destination} booked from {request.check_in_date} to {request.check_out_date}."
        )
    
    def CancelHotel(self, request, context):
        # Cancelar o hotel com o hotel_id fornecido
        return protocolo_pb2.CancelHotelResponse(
            status="Success",
            message=f"Hotel reservation {request.hotel_id} canceled."
        )



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    protocolo_pb2_grpc.add_HotelServicer_to_server(HotelService(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
