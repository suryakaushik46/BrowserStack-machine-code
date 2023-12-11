
file_path="log_file.txt"
last_line=0
def read_file():
    last_position=0
    with open(file_path, "r") as file:
        
        while True:
            file.seek(last_position)
            update_in_file= file.readline()
            if(update_in_file):
                #we can send to web client from here
                print(update_in_file)
                pass
                
            time.sleep(1)
            last_position= file.tell()

read_file()