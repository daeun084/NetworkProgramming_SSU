# NetworkingProgramming_SSU_Week6
### Pickle

- `pickle.dumps()`
    - 직렬화 / encoding / pickling
    - 객체를 바이트 스트림으로 변환하는 것
- `pickle.loads()`
    - 역직렬화 / decoding / unpickling
    - 바이트 스트림을 객체로 복원하는 것
    - `pickle.load(f)` → file 객체를 역직렬화

### JSON

- `json.dumps()`
- `json.loads()`

<br>

### Compression

integrity 손실 없이 데이터의 사이즈를 줄이기 위함

python은 `zlib` 을 사용

- `zlib.compress(data)`
- `zlib.decompress(compressed)`

- `zlib.decompressobj(wbits)`
    - data decompress를 위한 기능을 제공하는 객체를 생성함
    - 해당 객체를 통해 데이터를 쪼개 일부만 decompress 할 수 있음
    - `obj.unused_data`
        - 해당 객체에서 decompress 하고 **남은 데이터**를 가리킴

### Network Exceptions

- `OSError`
    - operating system error
        - socket의 어떤 함수 호출에도 일어날 수 있음 (bind(), accept(), …)
- `socket.gaierror`
    - get address information error
        - `getaddrinfo()` 에서 발생하는 exception
- `socket.timeout`

<br>

# TLS란?
transport layer security

- public-key
    - 누구나 소유할 수 있는 키
    - encrypt message (메세지 암호화)
    - verify signature
- private-key
    - decrypt message (메세지 해독)
    - create signature

<br>

# SSL
- secure socket layer
- Netscape에 의해 생성됨
- 현재는 TLS로 대체됨
- 신뢰성을 위해 `TCP` protocol 사용
- handshake를 통해 Application layer에 security service를 지원함
    - `handshake` protocol
    - `change cipher spec` protocol
    - `alert` protocol
- `SSL Session`
    - ssl-connection은 ssl-session 하나와 관련됨
    - handshake protocol에 의해 생성됨
    - **cryptographic parameter set**을 정의
- 공유된 개인 키를 활용해 **MAC**을 사용함
- 대칭 암호화를 사용함 → `**symmetric encryption**`
    - 공유된 개인 키를 사용해 (handshake protocol에 의해 생성됨)

<br>

### SSL Handshake
client-server connection (TCP Handshake)가 끝난 후 수립됨

[HTTPS 통신과정 쉽게 이해하기 #3(SSL Handshake, 협상)](https://aws-hyoh.tistory.com/39)

1. **Client Hello**
    - cipher suite(list), session ID, ssl protocol version, initial random number 전달
2. **Server Hello**
    - cipher suite (client가 보낸 리스트 중 하나를 골라서 client에게 전달함)
3. **Certificate**
    - 자신의 SSL 인증서를 Client에게 전달
    - 인증서는 공개키를 포함하며, 개인키는 Server에게 있음
    - **인증서는 CA의 개인키로 암호화되어있음**
    - Client는 CA의 공개키를 사용해 인증서를 복호화함 → 인증서 검증
4. **Server key exchange**
    - Server의 공개키가 인증서 내부에 없는 경우, 서버가 직접 공개키를 전달함
    - → Client는 Server의 공개키를 확보
    - server hello done
5. **Client key exchange**
    - Client는 대칭키를 생성한 후 서버의 공개키로 이를 암호화함
    - 이 대칭키를 서버에게 전달함
    - → certificate verify
6. **Change cipher spec**
    - client, server가 서로에게 packet을 보내, 정보를 모두 교환함
7. **Finished**
    - “finished” packet을 보내 handshake를 종료


→ Client와 Server는 동일한 대칭키를 소유하게 되며, 이를 통해 메세지를 암호화해 주고받을 수 있게 됨

<br>

### SSL 동작

1. 서버가 CA(인증기관)에 인증을 요청함
2. CA는 해당 서버를 검증한 후, 서버의 **정보와 공개 키를 개인 키로 암호화** 해 **인증서**를 제작함
3. CA가 서버에게 인증서를 발급함
4. CA는 클라이언트에게 본인의 개인키를 제공하며 이는 브라우저에 내장됨
5. 클라이언트가 서버에게 접속을 요청함
6. 서버가 클라이언트에게 인증서를 제공함
7. 클라이언트는 CA의 공개키로 인증서를 검증함
8. 클라이언트는 인증서를 통해 사이트 정보와 공개키를 획득함
9. 획득한 서버의 공개키로 대칭키를 암호화해 서버에 전달함
10. 서버는 개인키로 해당 대칭키를 해독해 획득함
11. 대칭키를 사용해 클라이언트와 서버가 통신을 주고받음

<br><br>

# TLS

SSL은 application layer와 transport layer 사이에 있기 때문에 IP addr, port# 을 보호할 수 없음

- TLS fails to protect
    - use `TOR` for avoiding tracking

### TLS Handshake

1. **Client hello**
    - TLS Version
    - Client Random Num
    - Session ID
        - 매번 연결할 때마다 handshake를 진행하는 것은 비효율적이니, 최초 한 번의 handshake를 할 때 ID를 발급해 사용함
            - 최초 session ID = 0 이나, handshake를 하며 서버로부터 ID를 받아옴
            - 해당 정보를 로컬에 저장해뒀다가 handshake를 또 할 일이 생기면 로컬에서 ID를 꺼내 서버에게 패킷을 보냄
2. **Server Hello**
    - TLS Version
    - Server Random Num
    - 암호화 방식, Session ID(유효한)
3. Server : Certificate를 Client에게 보냄
    - 클라이언트는 해당 인증서의 무결성을 검증함
4. Client Key Exchange
5. ... 


<br><br>

# Certification
누구나 CA의 공개키를 사용해 인증서를 검증할 수 있음
→ CA가 개인키를 사용해 인증서를 암호화하기 때문
즉, 누구나 브라우저의 정보와 공개키를 얻을 수 있음


🔎 **인증서의 역할**
- 데이터 암호화
- 웹 사이트의 신뢰성을 보장함 (신원 검증)

<br>

🔎 Not before / Not after <br>
- client가 인증서가 유효한지 아닌지를 판단하는 지표
