# NetworkingProgramming_SSU_Week5

<br>

# DNS


domain name system

ip address를 알기 위해 사용함 → naming system <br>
port num = `53` <br>
hostname → ipAddr <br>

`gethostbyname()` → `socket.gethostbyname(’maps.google.com’)`


- DHCP
    - dynamic host configuration protocol

dnspython

```python
resolve(qname, rdtype=<>, rdclass=<>, tcp=False, source=None, raise_on_no_answer=True,source_port=0, lifetime=None, search=None)
```

answer = dns.resolver.resolve(…)

<br><br>

# Bytes And String


- `bytes()`
    - bytes([1, 2]) → string으로 변환
    - `list()` 로 다시 변환 가능
- `pack()`
    - **struct** module
        - big-endian : “**>i**”
        - little-endian : “**<i**”
    
    `struct.pack(’<i’, 100)` → little endian으로 
    
<br><br>

# Framing And Quoting

### 1. Use SHUTDOWN

half-close

- `sc.shutdown(socket.SHUT_WR)`
    - recv만 진행함 / eof를 만나면 break
- `sc.shutdown(socket.SHUT_RD)`
    - send만 진행하며, 더 이상 보낼 데이터가 없으면 EOF를 보냄

### 2. Use recv() loop

```python
def recvall(sock, length):
	data = ' '
	while len(data) < length:
		more = sock.recv(length - len(data))
		if not more:
			raise EOFError('socket closed {} bytes into a {}-byte'
				' message'.format(len(data), length))
		data += more
return data
```

### 3. Framing each block of data

각 블럭의 길이를 Indicate함 → 받는 사람이 어느 크기의 데이터를 받을지 확인

- `put_block(sock, message)`
    - message : `header_struct + message` 로 구조화됨
    - header_struct : message length 정보 포함함
- `get_block(sock, message)`
    - header_struct에서 length를 찾음
    - `recvall(sock, header_struct.size)` 를 통해 데이터 수신