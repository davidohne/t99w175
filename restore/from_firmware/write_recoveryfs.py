import os
import time
import subprocess

# Configuration
python_binary = "python3.12"  # Python binary/version to use
vid = "13fb"
pid = "eafd"
input_file = "recoveryfs.bin" # Location of the RECOVERYFS image file on your filesystem
start_sector = 68608  # **** ATTENTION -> THIS HAS TO BE CHANGED ACCORDING TO YOUR PARTITION TABLE **** 
sectors_per_chunk = 2048
sector_size = 4096  
chunk_size = sectors_per_chunk * sector_size 
output_dir = "recoveryfs_write_chunks"  # Directory to store splitted chunks

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def split_file():
    with open(input_file, 'rb') as file:
        chunk_index = 1
        while True:
            chunk_data = file.read(chunk_size)
            if not chunk_data:
                break

            chunk_file_path = os.path.join(output_dir, f"recoveryfs_chunk{chunk_index}.bin")
            with open(chunk_file_path, 'wb') as chunk_file:
                chunk_file.write(chunk_data)
            chunk_index += 1

def write_chunk(start_sector, chunk_file_path):
    command = f"{python_binary} edl ws {start_sector} {chunk_file_path} --vid={vid} --pid={pid}"
    print(f"Executing command: {command}")

    process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    error_count = 0
    success = False
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            if "USBError(19, 'No such device" in output:
                error_count += 1
            if "Wrote" in output and f"to sector {start_sector}" in output:
                success = True
        if error_count > 10:
            process.terminate()
            print("Too many USB errors. Command terminated.")
            return False  

    return success

def write_chunks_to_device():
    chunks = sorted([f for f in os.listdir(output_dir) if f.startswith("recoveryfs_chunk")], key=lambda x: int(x.replace('recoveryfs_chunk', '').replace('.bin', '')))
    current_start_sector = start_sector
    for chunk_index, chunk in enumerate(chunks):
        chunk_file_path = os.path.join(output_dir, chunk)
        successful = write_chunk(current_start_sector, chunk_file_path)
        while not successful:
            print(f"Failed to write chunk {chunk}. Retrying...")
            time.sleep(2)  
            successful = write_chunk(current_start_sector, chunk_file_path)

        actual_chunk_size = os.path.getsize(chunk_file_path)
        sectors_written = (actual_chunk_size + sector_size - 1) // sector_size
        current_start_sector += sectors_written

if __name__ == "__main__":
    split_file()  
    write_chunks_to_device()  

