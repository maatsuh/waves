# matsuh i love you

import socket
import time
import math
import random
import os
import threading

# ANSI
CLEAR = "\033[2J\033[H"
HIDE = "\033[?25l"
SHOW = "\033[?25h"
RESET = "\033[0m"

# Cores do dia
DAY_SKY = "\033[97m"
DAY_WAVE1 = "\033[96m"
DAY_WAVE2 = "\033[36m"
DAY_WAVE3 = "\033[34m"
DAY_DEEP = "\033[94m"

# Cores do entardecer
SUNSET_SKY = "\033[93m"
SUNSET_WAVE1 = "\033[33m"
SUNSET_WAVE2 = "\033[91m"
SUNSET_WAVE3 = "\033[35m"
SUNSET_DEEP = "\033[34m"

# Cores da noite
NIGHT_SKY = "\033[90m"
NIGHT_WAVE1 = "\033[34m"
NIGHT_WAVE2 = "\033[94m"
NIGHT_WAVE3 = "\033[35m"
NIGHT_DEEP = "\033[30m"

# Cores do amanhecer
DAWN_SKY = "\033[95m"
DAWN_WAVE1 = "\033[33m"
DAWN_WAVE2 = "\033[36m"
DAWN_WAVE3 = "\033[34m"
DAWN_DEEP = "\033[94m"

# Cores especiais
YELLOW = "\033[93m"
WHITE_BRIGHT = "\033[97m"

# Sol ASCII
SUN = [
    "  \\|/  ",
    " --O-- ",
    "  /|\\  ",
]

# Lua ASCII
MOON = [
    "  _  ",
    " ( ) ",
    "  ~  ",
]

def send_chunk(conn, data):
    chunk = f"{len(data.encode('utf-8')):x}\r\n{data}\r\n"
    conn.sendall(chunk.encode("utf-8"))

def is_browser(req: str) -> bool:
    ua = req.lower()
    browsers = [
        "mozilla",
        "chrome",
        "safari",
        "firefox",
        "edge",
        "opera"
    ]
    return any(b in ua for b in browsers)

def handle(conn):
    try:
        req = conn.recv(2048).decode("utf-8", errors="ignore")

        if not req.startswith("GET /waves"):
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
            return

        # 🔁 SOMENTE navegador redireciona
        if is_browser(req):
            conn.sendall(
                b"HTTP/1.1 302 Found\r\n"
                b"Location: https://github.com/maatsuh/waves\r\n"
                b"Content-Length: 0\r\n\r\n"
            )
            return

        # Terminal / scripts → animação normal
        conn.sendall(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"Transfer-Encoding: chunked\r\n\r\n"
        )

        send_chunk(conn, HIDE)

        frame = 0
        cycle_length = 200

        while True:
            output = "\n"
            width = 70
            height = 20

            cycle_pos = (frame % cycle_length) / cycle_length

            if cycle_pos < 0.35:
                sky, wave1, wave2, deep = DAY_SKY, DAY_WAVE1, DAY_WAVE2, DAY_DEEP
                phase = 0
            elif cycle_pos < 0.45:
                sky, wave1, wave2, deep = SUNSET_SKY, SUNSET_WAVE1, SUNSET_WAVE2, SUNSET_DEEP
                phase = 1
            elif cycle_pos < 0.75:
                sky, wave1, wave2, deep = NIGHT_SKY, NIGHT_WAVE1, NIGHT_WAVE2, NIGHT_DEEP
                phase = 2
            else:
                sky, wave1, wave2, deep = DAWN_SKY, DAWN_WAVE1, DAWN_WAVE2, DAWN_DEEP
                phase = 3

            if phase == 2:
                stars = "".join(
                    random.choice(["*", ".", "·", "✦"]) if random.random() < 0.03 else " "
                    for _ in range(width)
                )
                output += f"{DAY_SKY}{stars}{RESET}\n"

            sun_x = sun_y = moon_x = moon_y = -10

            if cycle_pos < 0.45:
                p = cycle_pos / 0.45
                sun_x = int(5 + (width - 15) * p)
                sun_y = int(10 - 9 * math.sin(p * math.pi))

            if cycle_pos >= 0.45 or cycle_pos < 0.05:
                p = (cycle_pos - 0.45) / 0.55 if cycle_pos >= 0.45 else (cycle_pos + 0.55) / 0.55
                moon_x = int(5 + (width - 15) * p)
                moon_y = int(10 - 9 * math.sin(p * math.pi))

            for row in range(height):
                line = ""
                for col in range(width):
                    char = " "
                    color = ""

                    for sy, sline in enumerate(SUN):
                        for sx, schar in enumerate(sline):
                            if schar != " " and col == sun_x + sx - 3 and row == sun_y + sy - 1:
                                char, color = schar, YELLOW

                    for my, mline in enumerate(MOON):
                        for mx, mchar in enumerate(mline):
                            if mchar != " " and col == moon_x + mx - 2 and row == moon_y + my - 1:
                                char, color = mchar, WHITE_BRIGHT

                    if char != " ":
                        line += f"{color}{char}{RESET}"
                        continue

                    wave = (
                        1.5 * math.sin((col * 0.1) + (frame * 0.12)) +
                        math.sin((col * 0.05) + (frame * 0.08) + 1) +
                        0.8 * math.sin((col * 0.15) + (frame * 0.15) + 2)
                    )

                    water = 12 + wave

                    if row < water - 1:
                        line += " "
                    elif row < water:
                        line += "~"
                    elif row < water + 1:
                        line += "▄"
                    elif row < water + 2:
                        line += "█"
                    elif row < water + 4:
                        line += "▓"
                    else:
                        line += "░"

                if row < 10:
                    output += f"{sky}{line}{RESET}\n"
                elif row < 14:
                    output += f"{wave1}{line}{RESET}\n"
                else:
                    output += f"{deep}{line}{RESET}\n"

            send_chunk(conn, CLEAR)
            send_chunk(conn, output)

            frame += 1
            time.sleep(0.1)

    except:
        pass
    finally:
        try:
            send_chunk(conn, SHOW)
            conn.sendall(b"0\r\n\r\n")
        except:
            pass
        conn.close()

def main():
    port = int(os.environ.get("PORT", 80))

    print(f"""
curl http://localhost:{port}/waves
Porta: {port}
""")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.listen(100)

        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=handle,
                args=(conn,),
                daemon=True
            ).start()

if __name__ == "__main__":
    main()
