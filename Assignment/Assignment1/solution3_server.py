import random
import socket

# comment for client
win_comment = 'Congratulations you did it.\n'
up_comment = 'You Guessed too high!\n'
down_comment = 'You guessed too small!\n'
end_comment = "User don't start Game! End the Connection\n"
attempt_comment = 'The Attempt to play is over. End the connection\n'

# flog for game
game = False

MAX_BYTES = 1024 * 1024


def server():
    # make socket
    try:
        # use IPv4, TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as e:
        print("Socket Error:", e)
        exit(0)

    # bind socket
    try:
        s.bind(('127.0.0.1', 8080))
    except socket.error as e:
        print("Bind Error:", e)
        exit(0)

    # listen socket
    s.listen(1)
    print('Listening on {}:{}'.format(s.getsockname()[0], s.getsockname()[1]))

    # accept client socket
    try:
        sc, addr = s.accept()
        print('Accepted connection from {}:{}'.format(addr[0], addr[1]))
    except socket.error as e:
        print("Socket Accept Error:", e)
        exit(0)

    # count for client's attempt
    count = 0

    # make random number
    x = random.randint(1, 10)
    print("x=", x)

    # inform client about game and recv 'start'
    while True:
        sc.sendall('Guess the Number! Would you start the game?: '.encode('utf-8'))

        try:
            start_request, addr = sc.recvfrom(MAX_BYTES)
            if start_request.decode('utf-8') == 'start':
                # if client input start, start the game
                global game
                game = True
            else:
                # if client doesn't input start, end the connection
                print(end_comment)
                sc.sendall(end_comment.encode('utf-8'))
                s.close()
                sc.close()
            break

        except socket.error as e:
            print("Socket Error while receiving message:", e)

    # start guess the number game
    while (game):
        # client attempt 5 over
        if count >= 5:
            game = False
            sc.sendall(attempt_comment.encode('utf-8'))
            print(attempt_comment)
            break

        # send client for guess the number question
        sc.sendall('[Guess the number]: '.encode('utf-8'))

        # recv from client the guess number And parse it to int
        response = sc.recv(MAX_BYTES)
        guess = int(response.decode('utf-8'))

        # filtering the input number range
        if guess > 10 or guess < 1:
            sc.sendall('Invalid Guess Num. Try again\n'.encode('utf-8'))
            continue

        # print guess number from client
        print("[Client's Guess Number]: ", guess)

        # check the guess num and the random num
        if guess == x:
            sc.sendall(win_comment.encode('utf-8'))
            print('The Client win the Game. End the connection')
            break
        elif guess < x:
            sc.sendall(down_comment.encode('utf-8'))
        elif guess > x:
            sc.sendall(up_comment.encode('utf-8'))

        # check attempt count
        count += 1

    # close socket connection
    s.close()
    sc.close()


if __name__ == '__main__':
    server()
