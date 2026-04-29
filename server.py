
import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc

class CalculatorServicer(calculator_pb2_grpc.CalculatorServicer):
    #Qui è contenuta l'implementazione effettuva della calcolatrice
    #Con tutte le funzioni che può utilizzare
    
    def Add(self, request, context):
        r = request.operand1 + request.operand2
        return calculator_pb2.Result(result=r)
        
    def Subtract(self, request, context):
        r = request.operand1 - request.operand2
        return calculator_pb2.Result(result=r)
        
    def Multiply(self, request, context):
        r = request.operand1 * request.operand2
        return calculator_pb2.Result(result=r)
        
    #Nella divisione gestisco il caso della divisione per 0
    def Divide(self, request, context):
        if request.operand2 != 0:
            r = request.operand1 / request.operand2
            error = None
            return calculator_pb2.Result(result=r)
        else:
            r = 0
            error="Errore, divisione per 0 non permessa!!"
        return calculator_pb2.Result(
            result = r,
            error = error
        )

def serve():
    #Avvio il server gRPC
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    #Registro servizio e server da usare
    calculator_pb2_grpc.add_CalculatorServicer_to_server(
        CalculatorServicer(),
        server
    )
    
    #Bind
    server.add_insecure_port("[::]:" + port)
    #Avvio del server
    server.start()
    print(f"Server Calcolatrice avviato sulla porta: {port}")
    
    #Attendo terminazione da terminale
    server.wait_for_termination()
    
if __name__ == "__main__":
    serve()
    
    