# bit_converter.py

# Convert binary input to binary output with variable byte lengths.

class BitConverter:
    
    # Internal state set by ctor.
    __input_bit_count:int
    __output_bit_count:int

    __input_max:int

    # Working values.
    __current_output_bit_index:int      # Index of the current bit of the output. LSB is index 0, MSB is index (__output_bit_count - 1).
    __current_output_running_total:int  # The running total value of the current output byte.

    # Ctor. Takes input and output bit counts, raises exceptions when the bit count is <= 0 or would be large enough to overflow a 32-bit integer.
    def __init__(self, input_bit_count:int, output_bit_count:int):
        if input_bit_count in range(1, 32):
            self.__input_bit_count = input_bit_count
            self.__input_max = 2**self.__input_bit_count - 1
        else:
            raise Exception("Input bit count is out of range.")

        if output_bit_count in range(1, 32):
            self.__output_bit_count = output_bit_count
        else:
            raise Exception("Output bit count is out of range.")

        self.__reset_output()
    
    def __reset_output(self):
        self.__current_output_bit_index = self.__output_bit_count - 1
        self.__current_output_running_total = 0

    def __add_bit_to_output(self, bit_value:int):
        output_byte = 0

        # If the bit's value is 1, it changes the total. If 0, it doesn't, but the bit index still moves.
        if bit_value == 1:
            self.__current_output_running_total += (2**self.__current_output_bit_index)
        
        self.__current_output_bit_index -= 1

        # If an output byte was completed, return True and the final total.
        if self.__current_output_bit_index == -1:
            output_byte = self.__current_output_running_total
            self.__reset_output()
            return True, output_byte
    
        return False, -1
    
    def __consume_input(self, input_byte:int):
        output_bytes = []

        # for each bit in the input byte, starting from MSB to LSB...
        for input_bit_index in range(self.__input_bit_count - 1, -1, -1):
            # get the bit value
            bit = (input_byte >> input_bit_index) % 2

            # add the bit to the current output and catch the return values
            hasOutput, value = self.__add_bit_to_output(bit)
            
            # if a new output byte was created, add it to the output list
            if hasOutput:
                output_bytes.append(value)
        
        return output_bytes

    # Convert a list of input bytes to a list of output bytes along with the number of padding bytes that were added to round off the last output byte.
    def convert(self, input_bytes:list):
        self.__reset_output()
        
        output_bytes = []
        padding_bit_count = 0

        # Consume each input byte in the sequence and add the resulting output bytes to the output list.
        for input_byte in input_bytes:
            if input_byte in range(0, self.__input_max + 1):
                output_bytes.extend(self.__consume_input(input_byte))
            else:
                raise Exception("Input byte value was out of range for the byte size.")
        
        # If the output bit index has not been reset (need to add padding bits to complete the last byte),
        if (self.__current_output_bit_index != self.__output_bit_count - 1):
            # Fill the rest of the output with zeros.
            self.__current_output_running_total << self.__current_output_bit_index
            # Add it to the output list.
            output_bytes.append(self.__current_output_running_total)
            padding_bit_count = self.__current_output_bit_index + 1

        return output_bytes, padding_bit_count

    # Create a new BitConverter with swapped bit counts (for performing the inverse en/decode operation).
    def create_inverse_converter(self):
        return BitConverter(self.__output_bit_count, self.__input_bit_count)
