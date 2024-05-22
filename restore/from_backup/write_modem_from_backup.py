import os
import time
import subprocess

# Configuration
python_binary = "python3.12"  # Python binary/version to use
vid = "13fb"
pid = "eafd"
output_dir = "modem_chunks" 
start_sector = 17024 # **** ATTENTION -> THIS HAS TO BE CHANGED ACCORDING TO YOUR PARTITION TABLE ****
sectors_per_chunk = 2048  

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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
    chunks = sorted([f for f in os.listdir(output_dir) if f.endswith(".bin")], key=lambda x: int(x.replace('modem_chunk', '').replace('.bin', '')))
    current_start_sector = start_sector
    for chunk_index, chunk in enumerate(chunks):
        chunk_file_path = os.path.join(output_dir, chunk)
        successful = write_chunk(current_start_sector, chunk_file_path)
        while not successful:
            print(f"Failed to write chunk {chunk}. Retrying...")
            time.sleep(2)  
            successful = write_chunk(current_start_sector, chunk_file_path)

        current_start_sector += sectors_per_chunk

if __name__ == "__main__":
    write_chunks_to_device()  

