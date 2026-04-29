import grpc
from concurrent import futures
import calculator_pb2
import calculator_pb2_grpc
from random import randint, choice

operations = ["+", "-","*", "/"]

"""
Questa funzione prende un operazione casuale tra delle stringhe e la esegue con dei
numeri casuali, restituendo la risposta, l'operatore e gli operandi
"""

def run_random_operation(stub):
    
    num1 = randint(0,500)
    num2 = randint(0,500)
    
    op = choice(operations)
    
    if op == "+":
        answer = stub.Add(calculator_pb2.BinaryOperation(operand1 = num1, operand2 = num2))
    elif op == "-":
        answer = stub.Subtract(calculator_pb2.BinaryOperation(operand1 = num1, operand2 = num2))
    elif op == "*":
        answer = stub.Multiply(calculator_pb2.BinaryOperation(operand1 = num1, operand2 = num2))
    elif op == "/":
        answer = stub.Divide(calculator_pb2.BinaryOperation(operand1 = num1, operand2 = num2))
    else:
        raise ValueError(f"Operatore non valido: {op}")

    return answer, op, num1, num2


def run():
    #Creo un canale di comunicazione verso il server
    with grpc.insecure_channel("localhost:50051") as channel:
        #Creo lo stub del client, quindi un Proxy
        stub = calculator_pb2_grpc.CalculatorStub(channel)
        
        #Genero nel client 10 operazioni casuali con numeri casuali
        print("Calcolatrice gRPC in funzione\n")
        
        for i in range(1,21):
            answer, op, num1, num2 = run_random_operation(stub)
            print(f"Operazione {i}: {num1} {op} {num2} = {answer.result}")
            if answer.error:
                print(f"C'è un errore: {answer.error}")
                
if __name__ == "__main__":
    run()
    
        
    