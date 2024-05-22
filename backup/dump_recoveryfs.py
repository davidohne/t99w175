import os
import time
import subprocess

# Configuration
python_binary = "python3.12"  # Python binary/version to use
vid = "13fb"
pid = "eafd"
output_dir = "recoveryfs_chunks"  
start_sector = 68608  # **** ATTENTION -> THIS HAS TO BE CHANGED ACCORDING TO YOUR PARTITION TABLE ****
total_sectors = 31168  # **** ATTENTION -> THIS HAS TO BE CHANGED ACCORDING TO YOUR PARTITION TABLE ****
sectors_per_read = 2048  

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def run_edl_command(start_sector, num_sectors, chunk_index):
    output_file = f"{output_dir}/recoveryfs_chunk{chunk_index}.bin"
    command = f"{python_binary} edl rs {start_sector} {num_sectors} {output_file} --vid={vid} --pid={pid}"
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
            if f"Dumped sector {start_sector} with sector count {num_sectors}" in output:
                success = True
        if error_count > 10:
            process.terminate()
            print("Too many USB errors. Command terminated.")
            break

    if success:
        print(f"Successfully dumped sector {start_sector} with sector count {num_sectors} as {output_file}.")
        return True
    else:
        print(f"Failed to dump sector {start_sector}. Retrying...")
        return False

def read_partition():
    current_start_sector = start_sector  
    remaining_sectors = total_sectors  

    while remaining_sectors > 0:
        current_sectors_per_read = min(sectors_per_read, remaining_sectors)  
        successful = False
        while not successful:
            successful = run_edl_command(current_start_sector, current_sectors_per_read, (current_start_sector - start_sector) // sectors_per_read + 1)
            if not successful:
                time.sleep(2)  

        current_start_sector += current_sectors_per_read  
        remaining_sectors -= current_sectors_per_read 

if __name__ == "__main__":
    read_partition()

