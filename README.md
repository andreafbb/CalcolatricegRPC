# CalcolatricegRPC — Calcolatrice Distribuita con gRPC Unary Calls

## Descrizione dell'esercizio

L'esercizio richiede di implementare una calcolatrice distribuita client/server usando **gRPC con chiamate unarie (unary RPC)**.

Il server espone quattro operazioni aritmetiche di base (addizione, sottrazione, moltiplicazione, divisione) come RPC remote. Il client genera casualmente 20 operazioni con operandi casuali tra 0 e 500, le esegue tutte chiamando i metodi del server via stub gRPC, e stampa i risultati. La divisione gestisce il caso particolare della divisione per zero restituendo un messaggio di errore anziché causare un'eccezione.

L'obiettivo è:
- Definire il contratto di comunicazione in un file `.proto` con quattro RPC unarie
- Implementare il server con le quattro operazioni matematiche e gestione degli errori
- Implementare il client che sceglie casualmente operazione e operandi, chiama lo stub e stampa il risultato

---

## Architettura e workflow

```
client.py                                        server.py
    │                                                 │
    │  ──── BinaryOperation(operand1, operand2) ──▶   │
    │       (chiamata unaria: una richiesta,           │
    │        una risposta, poi la connessione          │
    │        viene chiusa)                             │
    │                                                 │  esegue operazione
    │                                                 │  gestisce /0
    │  ◀──── Result(result, error) ──────────────────  │
    │                                                 │
    │  (ripete 20 volte con operazione e              │
    │   operandi casuali)                             │
```

Il flusso per ogni operazione:
1. Il client sceglie casualmente un operatore tra `["+", "-", "*", "/"]` e due operandi tra 0 e 500
2. Costruisce un messaggio `BinaryOperation` e chiama il metodo corrispondente sullo stub
3. Lo stub serializza la richiesta, la invia al server, e blocca in attesa della risposta
4. Il server deserializza, esegue il calcolo, costruisce il `Result` e lo rispedisce
5. Il client riceve il `Result`, stampa operazione e risultato, e passa alla successiva

---

## File del progetto

### `calculator.proto`

Definisce il contratto gRPC. Contiene:

- **Servizio `Calculator`** con quattro RPC unarie:
  ```protobuf
  rpc Add(BinaryOperation) returns (Result) {}
  rpc Subtract(BinaryOperation) returns (Result) {}
  rpc Multiply(BinaryOperation) returns (Result) {}
  rpc Divide(BinaryOperation) returns (Result) {}
  ```
  Ogni RPC è **unaria**: il client invia un singolo messaggio e riceve una singola risposta.

- **Messaggio `BinaryOperation`** (operandi della richiesta):
  - `operand1` (int32): primo operando
  - `operand2` (int32): secondo operando

- **Messaggio `Result`** (risposta del server):
  - `result` (double): risultato dell'operazione
  - `error` (string): eventuale messaggio di errore (usato per la divisione per zero)

---

### `server.py`

Implementa la logica del server gRPC.

**Classe `CalculatorServicer`:** eredita da `calculator_pb2_grpc.CalculatorServicer` e implementa i quattro metodi RPC:

- **`Add`**: ritorna `operand1 + operand2` come `Result`
- **`Subtract`**: ritorna `operand1 - operand2`
- **`Multiply`**: ritorna `operand1 * operand2`
- **`Divide`**: verifica che `operand2 != 0`:
  - Se `operand2 != 0`: calcola e restituisce la divisione con risultato come `double`
  - Se `operand2 == 0`: restituisce `Result(result=0, error="Errore, divisione per 0 non permessa!!")` senza sollevare eccezione

**Avvio del server (`serve`):**
- Crea un server gRPC con `ThreadPoolExecutor(max_workers=10)`
- Registra il servicer con `add_CalculatorServicer_to_server`
- Bind su porta `50051`
- Avvia e attende terminazione con `wait_for_termination()`

---

### `client.py`

Implementa il client gRPC con esecuzione casuale di operazioni.

**Lista delle operazioni:** `operations = ["+", "-", "*", "/"]`

**Funzione `run_random_operation(stub)`:**
- Genera `num1` e `num2` come interi casuali tra 0 e 500 con `randint(0, 500)`
- Sceglie casualmente un operatore con `choice(operations)`
- Costruisce un `BinaryOperation(operand1=num1, operand2=num2)` e chiama il metodo corrispondente sullo stub:
  - `"+"`  → `stub.Add(...)`
  - `"-"`  → `stub.Subtract(...)`
  - `"*"`  → `stub.Multiply(...)`
  - `"/"` → `stub.Divide(...)`
- Restituisce la tupla `(answer, op, num1, num2)` al chiamante

**Funzione `run()`:**
- Apre un canale insicuro verso `localhost:50051`
- Crea lo stub `CalculatorStub`
- Esegue un ciclo di **20 iterazioni** (da 1 a 20):
  - Chiama `run_random_operation(stub)`
  - Stampa `Operazione i: num1 op num2 = risultato`
  - Se `answer.error` è non vuoto, stampa anche il messaggio di errore (divisione per zero)

---

### `calculator_pb2.py` e `calculator_pb2_grpc.py`

File autogenerati da `protoc`. Non vanno modificati a mano.

- `calculator_pb2.py`: classi Python per i messaggi `BinaryOperation` e `Result`
- `calculator_pb2_grpc.py`: classe base `CalculatorServicer` e classe `CalculatorStub`

Per rigenerarli in caso di modifica al `.proto`:
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. calculator.proto
```

---

## Requisiti

- Python 3
- Librerie gRPC per Python:

```bash
pip install grpcio grpcio-tools
```

---

## Esecuzione

Apri **due terminali** nella cartella `CalcolatricegRPC/`.

**Terminale 1 — Avvia il server:**
```bash
python3 server.py
```
Output atteso:
```
Server Calcolatrice avviato sulla porta: 50051
```

**Terminale 2 — Avvia il client:**
```bash
python3 client.py
```
Output atteso (esempio, i valori cambiano ad ogni esecuzione):
```
Calcolatrice gRPC in funzione

Operazione 1: 342 + 17 = 359.0
Operazione 2: 100 / 0 = 0.0
C'è un errore: Errore, divisione per 0 non permessa!!
Operazione 3: 88 * 45 = 3960.0
...
```

---

## Concetti chiave

| Concetto | Dove si applica |
|---|---|
| Unary RPC gRPC | Quattro metodi in `calculator.proto`: una richiesta → una risposta |
| Stub gRPC come proxy locale | `CalculatorStub(channel)` in `client.py`: il client chiama metodi Python come se fossero locali |
| Gestione divisione per zero | `Divide` in `server.py`: restituisce `error` nel `Result` invece di lanciare eccezione |
| Operazioni casuali | `randint` e `choice` in `client.py` per simulare un carico di lavoro variabile |
| `ThreadPoolExecutor` nel server | Gestisce più client concorrenti grazie al thread pool gRPC |
