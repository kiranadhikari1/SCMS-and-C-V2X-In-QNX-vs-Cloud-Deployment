# Makefile for SCMS QNX Simulation
# Compiler and flags
CC = qcc
CFLAGS = -Wall -std=c99

# Source and output
SRC = src/SCMS_SIM.c
TARGET = scms_report

# Default build
all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

# Clean up build files
clean:
	rm -f $(TARGET) *.o *.csv *.txt

# Run the executable
run: $(TARGET)
	./$(TARGET)
