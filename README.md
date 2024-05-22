# EDL backup + restore scripts for T99W175 5G M.2 Modem

### ATTENTION ###
In every script the start_sector (in dump-scripts also the total_secors) are commented --> The scripts will not work unless you add your actual start sectors and total sectors to the script
How to find out start_sector and total_sectors? One possibility:
- Try to read the whole partition from the modem e.g.

```python3.12 edl r system system_read_test.bin --vid=13fb --pid=eafd```
- Before the USB Errors appear a line like the following will appear:

```Reading from physical partition 0, sector 64064, sectors 256```
- In this case 64064 is the start_sector and total_sectors is 256
