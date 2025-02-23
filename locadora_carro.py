from concurrent import futures
import grpc
import protocolo_pb2
import protocolo_pb2_grpc
import uuid

class CarRentalService(protocolo_pb2_grpc.CarRentalServicer):
    def BookCar(self, request, context):
        # Gerar um ID único para o aluguel de carro
        car_id = str(uuid.uuid4())  # Gerando um ID único com UUID
        
        return protocolo_pb2.CarResponse(
            status="Success",
            car_id=car_id,  # Inclui o car_id na resposta
            car_details=f"Car at {request.destination} booked from {request.pick_up_date} to {request.drop_off_date}."
        )
    
    def CancelCar(self, request, context):
        # Cancelar o carro com o car_id fornecido
        return protocolo_pb2.CancelCarResponse(
            status="Success",
            message=f"Car rental {request.car_id} canceled."
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
