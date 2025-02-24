import grpc
import time
import protocolo_pb2
import protocolo_pb2_grpc

def check_server_ready():
    while True:
        try:
            # Tente se conectar ao servidor
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = protocolo_pb2_grpc.TravelAgencyStub(channel)
                # Tentando um método simples para verificar a conectividade
                stub.BookTrip(protocolo_pb2.TripRequest())
            print("Servidor gRPC pronto para conexões!")
            break  # Sai do loop se a conexão for bem-sucedida
        except grpc.RpcError as e:
            print(f"Falha na conexão ao servidor: {e}. Tentando novamente...")
            time.sleep(2)  # Tente novamente após um pequeno atraso

# Funções de teste

def test_full_trip_reservation():
    try:
        request = protocolo_pb2.TripRequest(
            user_id="12345",
            trip_type="round_trip",
            origin="Curitiba",
            destination="São Paulo",
            departure_date="2024-10-10",
            return_date="2024-10-20",
            num_people=2
        )

        # Validação de dados ausentes
        if not request.user_id or not request.trip_type or not request.origin or not request.destination or not request.departure_date or not request.num_people:
            print("Erro: Dados ausentes na solicitação de viagem.")
            return protocolo_pb2.TripResponse(status="Failure", details="Dados ausentes na solicitação de viagem.")

        # Validação adicional para one_way (onde a data de volta pode ser ausente)
        if request.trip_type != "one_way" and not request.return_date:
            print("Erro: Data de retorno ausente na solicitação de viagem.")
            return protocolo_pb2.TripResponse(status="Failure", details="Data de retorno ausente para viagem de ida e volta.")

        print("Dados da viagem validados com sucesso.")

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = protocolo_pb2_grpc.TravelAgencyStub(channel)
            response = stub.BookTrip(request)

        if response.status == "Success":
            print("Reserva completa ok")
        else:
            print(f"Erro esperado não ocorreu: status recebido {response.status}")
    except Exception as e:
        print(f"Erro ao tentar reservar viagem completa: {e}")

def test_one_way_trip_reservation():
    try:
        request = protocolo_pb2.TripRequest(
            user_id="12345",
            trip_type="one_way",  
            origin="Curitiba",
            destination="São Paulo",
            departure_date="2024-10-10",
            return_date="",  
            num_people=2
        )

        # Validação de dados ausentes
        if not request.user_id or not request.trip_type or not request.origin or not request.destination or not request.departure_date or not request.num_people:
            print("Erro: Dados ausentes na solicitação de viagem.")
            return protocolo_pb2.TripResponse(status="Failure", details="Dados ausentes na solicitação de viagem.")

        # Validação adicional para one_way (onde a data de volta pode ser ausente)
        if request.trip_type != "one_way" and not request.return_date:
            print("Erro: Data de retorno ausente na solicitação de viagem.")
            return protocolo_pb2.TripResponse(status="Failure", details="Data de retorno ausente para viagem de ida e volta.")

        print("Dados da viagem validados com sucesso.")

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = protocolo_pb2_grpc.TravelAgencyStub(channel)
            response = stub.BookTrip(request)

        if response.status == "Success":
            print("Viagem somente ida ok")
        else:
            print(f"Erro esperado não ocorreu: status recebido {response.status}")
    except Exception as e:
        print(f"Erro ao tentar reservar viagem somente ida: {e}")

def test_missing_data_in_trip_request():
    try:
        request = protocolo_pb2.TripRequest(
            user_id="12345",
            trip_type="round_trip",
            origin="Curitiba",
            destination="São Paulo",
            departure_date="",  
            return_date="2024-10-20",
            num_people=2
        )

        # Validação de dados ausentes
        if not request.user_id or not request.trip_type or not request.origin or not request.destination or not request.departure_date or not request.num_people:
            print("Erro: Dados ausentes na solicitação de viagem.")
            return protocolo_pb2.TripResponse(status="Failure", details="Dados ausentes na solicitação de viagem.")

        # Validação adicional para one_way (onde a data de volta pode ser ausente)
        if request.trip_type != "one_way" and not request.return_date:
            print("Erro: Data de retorno ausente na solicitação de viagem.")
            return protocolo_pb2.TripResponse(status="Failure", details="Data de retorno ausente para viagem de ida e volta.")

        print("Dados da viagem validados com sucesso.")

        with grpc.insecure_channel('localhost:50051') as channel:
            stub = protocolo_pb2_grpc.TravelAgencyStub(channel)
            response = stub.BookTrip(request)

        if response.status == "Failure":
            print("Dados ausentes ok")
        else:
            print(f"Erro esperado não ocorreu: status recebido {response.status}")
    except Exception as e:
        print(f"Erro ao tentar reservar com dados ausentes: {e}")

# Função para rodar todos os testes
def run_all_tests():
    tests = [
        ("Teste de reserva completa", test_full_trip_reservation),
        ("Teste de viagem somente ida", test_one_way_trip_reservation),
        ("Teste de dados ausentes", test_missing_data_in_trip_request),
    ]

    for test_name, test_func in tests:
        print(f"\nIniciando {test_name}...")
        try:
            test_func()
        except Exception as e:
            print(f"Erro no {test_name}: {e}")

def run():
    check_server_ready()  # Verifique se o servidor está pronto antes de continuar
    
    print("Escolha qual teste deseja rodar:")
    print("1 - Teste de reserva completa")
    print("2 - Teste de viagem somente ida")
    print("3 - Teste de dados ausentes")
    print("4 - Rodar todos os testes")

    choice = input("Digite o número do teste: ")

    if choice == "1":
        test_full_trip_reservation()
    elif choice == "2":
        test_one_way_trip_reservation()
    elif choice == "3":
        test_missing_data_in_trip_request()
    elif choice == "4":
        run_all_tests()
    else:
        print("Opção inválida. Nenhum teste executado.")

if __name__ == "__main__":
    run()
