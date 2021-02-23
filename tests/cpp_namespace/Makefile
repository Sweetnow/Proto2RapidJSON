CC=g++
CCFLAGS=-Wall -Wextra -O0 -std=c++17
INCLUDES=-I ../../
EXEC=main

main.out: main.cpp
	@$(CC) $(CCFLAGS) $(INCLUDES) $^ -o $@

clean:
	@rm main.out